#!/usr/bin/env python3
"""
LLM Wiki Static Site Generator

Generates a beautiful, browsable HTML site from the wiki's markdown files.
Each HTML page links back to its source .md file for bidirectional association.

Usage:
    python3 scripts/generate-web.py
    python3 scripts/generate-web.py --serve   # Serve on :8080 after generating
"""

import os
import sys
import re
import json
import html
import webbrowser
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from functools import lru_cache

import yaml
import markdown


# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

WIKI_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WIKI_ROOT / "web" / "output"
SITE_NAME = "LLM 研究知识库"
SITE_SUBTITLE = "论文、概念与模型的长期研究档案"

TAG_COLORS = {
    'model': '#D4A04A',
    'architecture': '#7BB3CC',
    'speech-model': '#C97A7A',
    'rl': '#6B9B7D',
    'distillation': '#B88CC9',
    'on-policy': '#C9976A',
    'training': '#7AACC9',
    'inference': '#9BC96B',
    'alignment': '#C96B9B',
    'safety': '#CC6B6B',
    'agent': '#6BC9B3',
    'benchmark': '#C9B36B',
    'memory': '#8B7ACC',
    'multimodal': '#CC9B6B',
    'reasoning': '#6BB3C9',
    'full-duplex': '#C97AB3',
    'half-duplex': '#B39B6B',
    'end-to-end': '#6BC98B',
    'open-source': '#7AC97A',
    'company': '#C9C97A',
    'open-policy-distillation': '#B88CC9',
    'grpo': '#9B7AC9',
    'tool-use': '#6BC9C9',
    'synthetic-data': '#C9C96B',
    'post-training': '#7A9BC9',
    'pretraining': '#9B9B6B',
}

DEFAULT_TAG_COLOR = '#8B8D94'

TYPE_LABELS = {
    'entities': '实体',
    'concepts': '概念',
    'queries': '问答',
    'papers': '论文',
}

TYPE_DESCRIPTIONS = {
    'entities': '模型、机构、产品与重要对象',
    'concepts': '技术路线、方法、范式与研究主题',
    'queries': '围绕具体问题沉淀下来的研究回答',
}


# ═══════════════════════════════════════════════════════════════
# Page Loading & Indexing
# ═══════════════════════════════════════════════════════════════

def load_all_pages():
    pages = {}
    for page_type in ['entities', 'concepts', 'queries']:
        type_dir = WIKI_ROOT / page_type
        if not type_dir.exists():
            continue
        for md_file in sorted(type_dir.glob('*.md')):
            page = load_page(md_file, page_type)
            if page:
                pages[page['name']] = page
    return pages


@lru_cache(maxsize=1)
def load_allowed_tags():
    tags = set()
    schema_path = WIKI_ROOT / 'SCHEMA.md'
    if not schema_path.exists():
        return tags
    for line in schema_path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('- **') or ':' not in line:
            continue
        _, values = line.split(':', 1)
        tags.update(tag.strip() for tag in values.split(',') if tag.strip())
    return tags


def load_page(filepath, page_type):
    text = filepath.read_text(encoding='utf-8')

    meta = {}
    content = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
            content = parts[2].strip()

    return {
        'name': filepath.stem,
        'type': page_type,
        'title': meta.get('title', filepath.stem),
        'created': str(meta.get('created', '')),
        'updated': str(meta.get('updated', '')),
        'tags': meta.get('tags', []),
        'sources': meta.get('sources', []),
        'content': content,
        'md_relpath': f"{page_type}/{filepath.stem}.md",
    }


def split_frontmatter(text):
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, parts[2].strip()


def load_paper_page(md_file):
    text = md_file.read_text(encoding='utf-8', errors='ignore')
    meta, content = split_frontmatter(text)
    title, preview = paper_metadata(md_file)
    rel = md_file.relative_to(WIKI_ROOT / 'raw' / 'papers')
    date_match = re.match(r'(\d{4})/(\d{2})', str(rel))
    date_str = f"{date_match.group(1)}-{date_match.group(2)}" if date_match else ''
    arxiv_match = re.search(r'(\d{4}\.\d{4,5})(?:v\d+)?', text)
    clean_path = WIKI_ROOT / 'papers' / rel
    brief_path = WIKI_ROOT / 'paper-briefs' / rel
    brief_meta = {}
    brief_content = ''
    if brief_path.exists():
        brief_text = brief_path.read_text(encoding='utf-8', errors='ignore')
        brief_meta, brief_content = split_frontmatter(brief_text)
        if brief_meta.get('title_zh'):
            preview = get_preview(brief_content, 220) or preview
    return {
        'name': md_file.stem,
        'type': 'papers',
        'title': title,
        'title_zh': brief_meta.get('title_zh', ''),
        'created': date_str,
        'updated': '',
        'tags': ['paper', str(meta.get('source') or 'source')],
        'sources': [],
        'content': content,
        'brief_content': brief_content,
        'brief_relpath': f"paper-briefs/{rel.as_posix()}" if brief_path.exists() else '',
        'clean_relpath': f"papers/{rel.as_posix()}" if clean_path.exists() else '',
        'quality': brief_meta.get('quality', ''),
        'paper_type': brief_meta.get('paper_type', ''),
        'preview': preview,
        'md_relpath': f"raw/papers/{rel.as_posix()}",
        'relpath': rel.as_posix(),
        'url': meta.get('url', ''),
        'source': meta.get('source', ''),
        'arxiv_id': arxiv_match.group(1) if arxiv_match else md_file.stem,
    }


def load_all_papers():
    papers_dir = WIKI_ROOT / 'raw' / 'papers'
    if not papers_dir.exists():
        return []
    return [load_paper_page(md_file) for md_file in sorted(papers_dir.rglob('*.md'), reverse=True)]


def build_backlinks(pages):
    backlinks = defaultdict(set)
    for name, page in pages.items():
        links = re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', page['content'])
        for link in links:
            if link != name:
                backlinks[link].add(name)
    return {k: list(v) for k, v in backlinks.items()}


def build_concept_categories(pages):
    """Build subcategory -> [page names] for concepts, based on index.md."""
    categories = defaultdict(list)
    index_path = WIKI_ROOT / 'index.md'
    if not index_path.exists():
        return categories

    current_cat = None
    in_concepts = False
    for line in index_path.read_text().split('\n'):
        stripped = line.strip()
        # Detect "## Concepts" section
        if stripped == '## Concepts':
            in_concepts = True
            continue
        # Exit concepts section on next ## heading
        if stripped.startswith('## ') and stripped != '## Concepts':
            in_concepts = False
            current_cat = None
            continue
        if not in_concepts:
            continue
        # Parse subcategory headers like ### 'distillation' or ### agent
        if stripped.startswith('### '):
            cat_name = stripped[4:].strip().strip("'\"")
            current_cat = cat_name
        elif stripped.startswith('- [[') and current_cat:
            link_match = re.match(r'- \[\[([^\]|]+)', stripped)
            if link_match:
                link_name = link_match.group(1)
                if link_name in pages and pages[link_name]['type'] == 'concepts':
                    categories[current_cat].append(link_name)
    return categories


def _first(pages, name):
    return name if name in pages else ''


# ═══════════════════════════════════════════════════════════════
# Markdown Rendering
# ═══════════════════════════════════════════════════════════════

def render_markdown(text, pages):
    allowed_tags = load_allowed_tags()

    def resolve_wikilink(match):
        raw = match.group(1)
        pipe_idx = raw.find('|')
        if pipe_idx >= 0:
            link = raw[:pipe_idx].strip()
            display = raw[pipe_idx + 1:].strip()
        else:
            link = raw.strip()
            display = link

        if link in pages:
            p = pages[link]
            return f'<a class="wikilink" href="../{p["type"]}/{link}.html">{display}</a>'
        if link in allowed_tags:
            return f'<a class="wikilink tag-link" href="../tags.html#tag-{anchor_id(link)}">{display}</a>'
        return f'<span class="wikilink broken" title="Page not found">{display}</span>'

    text = re.sub(r'\[\[([^\]]+)\]\]', resolve_wikilink, text)

    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'codehilite'],
                           extension_configs={'codehilite': {'css_class': 'highlight', 'guess_lang': False}})
    return md.convert(text)


def clean_inline(text):
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_preview(content, max_len=260):
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('>') and not stripped.startswith('```'):
            stripped = clean_inline(stripped.lstrip('-0123456789. '))
            if not stripped or stripped == '---':
                continue
            if re.match(r'^(arXiv|Date|Authors|Affiliation|Code|GitHub|Paper|Source)\s*[:：|]', stripped, re.I):
                continue
            if re.match(r'^\|?[-:\s|]+\|?$', stripped):
                continue
            if len(stripped) > max_len:
                return stripped[:max_len] + '...'
            return stripped
    return ''


def get_headings(content, limit=5):
    headings = []
    for line in content.split('\n'):
        m = re.match(r'^(#{2,3})\s+(.+)$', line.strip())
        if not m:
            continue
        title = clean_inline(m.group(2))
        title = re.sub(r'^\d+(\.\d+)*\s*[.:、-]?\s*', '', title)
        if title and title not in headings:
            headings.append(title)
        if len(headings) >= limit:
            break
    return headings


def reading_minutes(content):
    body = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    count = len(re.sub(r'\s+', '', body))
    return max(1, round(count / 650))


def format_date(value):
    if not value:
        return '未标注'
    return str(value)


def page_summary_chips(page, max_items=4):
    headings = get_headings(page['content'], max_items)
    if not headings:
        headings = page['tags'][:max_items]
    return ''.join(f'<span class="summary-chip">{html.escape(h)}</span>' for h in headings)


def anchor_id(text):
    return re.sub(r'[^a-zA-Z0-9_-]+', '-', str(text)).strip('-') or 'section'


def paper_metadata(md_file):
    rel_text = md_file.read_text(encoding='utf-8', errors='ignore')
    meta, body = split_frontmatter(rel_text)
    rel_text = body[:2200]
    title = md_file.stem
    preview = ''
    if meta.get('title'):
        title = str(meta['title']).strip()
    for line in rel_text.split('\n'):
        stripped = clean_inline(line.strip())
        if not stripped:
            continue
        if line.startswith('# '):
            title = stripped.lstrip('# ').strip()
            continue
        if line.startswith('Title:'):
            title = stripped[6:].strip()
            continue
        if re.match(r'^(arXiv|Date|Authors|Affiliation|Code|GitHub|Paper|Source|Estimated tokens|Sections)\s*[:：|]', stripped, re.I):
            continue
        if not preview and not stripped.startswith('#') and len(stripped) > 30:
            preview = stripped
    if len(preview) > 220:
        preview = preview[:220] + '...'
    return title, preview


# ═══════════════════════════════════════════════════════════════
# HTML Generation
# ═══════════════════════════════════════════════════════════════

def tag_html(tag):
    color = TAG_COLORS.get(tag, DEFAULT_TAG_COLOR)
    return f'<span class="tag" style="--tag-color: {color}">{tag}</span>'


def tags_html(tags):
    return ' '.join(tag_html(t) for t in tags)


def relative_path_to_root(page_type=None):
    if page_type:
        return '../'
    return ''


def generate_nav(current_section=None, page_type=None):
    root = relative_path_to_root(page_type)
    sections = [
        ('home', '总览', f'{root}index.html', '⬡'),
        ('entities', '实体', f'{root}entities/index.html', '◆'),
        ('concepts', '概念', f'{root}concepts/index.html', '◇'),
        ('queries', '问答', f'{root}queries/index.html', '◈'),
        ('papers', '论文', f'{root}papers/index.html', '▤'),
    ]
    items = []
    for key, label, href, icon in sections:
        active = ' active' if key == current_section else ''
        items.append(f'<a href="{href}" class="nav-item{active}"><span class="nav-icon">{icon}</span>{label}</a>')
    return '\n'.join(items)


def html_head(title, current_section=None, page_type=None):
    root = relative_path_to_root(page_type)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {SITE_NAME}</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&family=Noto+Sans+SC:wght@300;400;500;600;700&family=JetBrains+Mono:ital,wght@0,400;0,500;1,400&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,800;1,9..144,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}static/wiki.css">
</head>
<body>
<aside id="sidebar">
<div class="sidebar-header">
<a href="{root}index.html" class="site-title">
<span class="title-icon">&#x2234;</span>
<span class="title-text">{SITE_NAME}</span>
</a>
<div class="site-subtitle">{SITE_SUBTITLE}</div>
</div>
<nav class="sidebar-nav">
{generate_nav(current_section, page_type)}
</nav>
<div class="sidebar-footer">
<div class="sidebar-search">
<div class="search-wrapper">
<svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
<input type="text" id="search-input" placeholder="搜索概念、模型、标签... /" autocomplete="off">
</div>
<div id="search-results" class="search-results"></div>
</div>
</div>
</aside>
<button id="sidebar-toggle" aria-label="打开导航">
<span></span><span></span><span></span>
</button>
<main id="main">'''


def html_foot(page_type=None):
    root = relative_path_to_root(page_type)
    return f'''</main>
<script>window.WIKI_ROOT = {json.dumps(root)};</script>
<script src="{root}static/wiki.js"></script>
</body>
</html>'''


# ── Home Page ──────────────────────────────────────────────

def generate_home(pages, backlinks, categories):
    entity_pages = [p for p in pages.values() if p['type'] == 'entities']
    concept_pages = [p for p in pages.values() if p['type'] == 'concepts']
    query_pages = [p for p in pages.values() if p['type'] == 'queries']
    paper_count = len(list((WIKI_ROOT / 'raw' / 'papers').rglob('*.md')))

    all_tags = defaultdict(int)
    for p in pages.values():
        for t in p['tags']:
            all_tags[t] += 1

    tag_cloud = ' '.join(
        f'<a href="tags.html" class="tag" style="--tag-color: {TAG_COLORS.get(t, DEFAULT_TAG_COLOR)}">{t} <small>{c}</small></a>'
        for t, c in sorted(all_tags.items(), key=lambda x: -x[1])[:32]
    )

    recent = sorted(pages.values(), key=lambda p: p['updated'] or '0', reverse=True)[:10]

    cat_cards = []
    for cat, count in [('实体', len(entity_pages)), ('概念', len(concept_pages)),
                        ('问答', len(query_pages)), ('论文', paper_count)]:
        icons = {'实体': '◆', '概念': '◇', '问答': '◈', '论文': '▤'}
        links = {'实体': 'entities/index.html', '概念': 'concepts/index.html',
                 '问答': 'queries/index.html', '论文': 'papers/index.html'}
        cat_cards.append(f'''
        <a href="{links[cat]}" class="stat-card">
            <div class="stat-icon">{icons[cat]}</div>
            <div class="stat-number">{count}</div>
            <div class="stat-label">{cat}</div>
        </a>''')

    recent_items = []
    for p in recent:
        chips = page_summary_chips(p, 3)
        recent_items.append(f'''
        <a href="{p['type']}/{p['name']}.html" class="recent-item">
            <span class="recent-type {p['type']}">{TYPE_LABELS.get(p['type'], p['type'])}</span>
            <span class="recent-main">
                <span class="recent-title">{html.escape(p['title'])}</span>
                <span class="recent-preview">{html.escape(get_preview(p['content'], 180))}</span>
                <span class="summary-chips">{chips}</span>
            </span>
            <span class="recent-date">{format_date(p['updated'])}</span>
        </a>''')

    focus_items = []
    for cat, names in sorted(categories.items(), key=lambda x: -len(x[1]))[:10]:
        focus_items.append(f'''
        <a href="concepts/index.html#cat-{anchor_id(cat)}" class="focus-item">
            <span>{html.escape(cat)}</span>
            <strong>{len(names)}</strong>
        </a>''')

    body = f'''
    <div class="home-header">
        <h1 class="home-title">{SITE_NAME}</h1>
        <p class="home-desc">{SITE_SUBTITLE}。当前沉淀 {len(pages)} 个知识页面、{paper_count} 篇论文源材料，覆盖模型架构、后训练、语音多模态、智能体与推理等方向。</p>
    </div>

    <div class="stats-grid">
        {''.join(cat_cards)}
    </div>

    <div class="home-grid">
        <section class="home-section">
            <h2 class="section-title">最近更新</h2>
            <div class="recent-list">
                {''.join(recent_items)}
            </div>
        </section>

        <section class="home-section">
            <h2 class="section-title">主题索引</h2>
            <div class="focus-grid">
                {''.join(focus_items)}
            </div>
            <h2 class="section-title secondary">高频标签</h2>
            <div class="tag-cloud">
                {tag_cloud}
            </div>
        </section>
    </div>
    '''

    return html_head('Home', 'home') + body + html_foot()


# ── Entity / Query Listing ─────────────────────────────────

def generate_listing(pages, page_type, title, description, current_section):
    type_pages = sorted(
        [p for p in pages.values() if p['type'] == page_type],
        key=lambda p: p['title'].lower()
    )

    if page_type == 'entities':
        cards = []
        for p in type_pages:
            preview = get_preview(p['content'], 320)
            cards.append(f'''
            <a href="{p['name']}.html" class="page-card">
                <div class="page-card-header">
                    <h3 class="page-card-title">{html.escape(p['title'])}</h3>
                    <span class="page-card-date">{format_date(p['updated'] or p['created'])}</span>
                </div>
                <p class="page-card-preview">{html.escape(preview)}</p>
                <div class="summary-chips">{page_summary_chips(p, 4)}</div>
                <div class="page-card-tags">{tags_html(p['tags'][:6])}</div>
            </a>''')
        grid = f'<div class="page-grid">{"".join(cards)}</div>'
    else:
        items = []
        for p in type_pages:
            items.append(f'''
            <a href="{p['name']}.html" class="list-item">
                <div class="list-item-main">
                    <h3>{html.escape(p['title'])}</h3>
                    <p>{html.escape(get_preview(p['content'], 340))}</p>
                    <div class="summary-chips">{page_summary_chips(p, 4)}</div>
                </div>
                <div class="list-item-meta">
                    <span class="list-item-type {p['type']}">{TYPE_LABELS.get(p['type'], p['type'])}</span>
                    <span class="list-item-date">{format_date(p['updated'] or p['created'])}</span>
                    <div class="page-card-tags">{tags_html(p['tags'][:4])}</div>
                </div>
            </a>''')
        grid = f'<div class="list-view">{"".join(items)}</div>'

    body = f'''
    <div class="listing-header">
        <div class="breadcrumb">
            <a href="../index.html">总览</a> <span class="sep">/</span>
            <span class="current">{title}</span>
        </div>
        <h1>{title}</h1>
        <p class="listing-desc">{description}，共 {len(type_pages)} 个页面。列表展示摘要、主要小节和标签，方便快速判断是否值得进入详情。</p>
    </div>
    {grid}
    '''

    return html_head(title, current_section, page_type) + body + html_foot(page_type)


# ── Concept Listing (grouped by category) ──────────────────

def generate_concept_listing(pages, categories):
    total = len([p for p in pages.values() if p['type'] == 'concepts'])
    uncat = [p for p in pages.values() if p['type'] == 'concepts' and
             not any(p['name'] in v for v in categories.values())]

    sections = []
    category_items = list(sorted(categories.items(), key=lambda x: (-len(x[1]), x[0].lower())))
    if uncat:
        category_items.append(('未归类', [p['name'] for p in uncat]))

    for cat, names in category_items:
        cat_pages = [pages[n] for n in names if n in pages]
        if not cat_pages:
            continue
        items = []
        for p in sorted(cat_pages, key=lambda x: x['title'].lower()):
            items.append(f'''
            <a href="{p['name']}.html" class="page-card compact">
                <div class="page-card-header compact">
                    <h3>{html.escape(p['title'])}</h3>
                    <span>{reading_minutes(p['content'])} 分钟</span>
                </div>
                <p>{html.escape(get_preview(p['content'], 280))}</p>
                <div class="summary-chips">{page_summary_chips(p, 3)}</div>
                <div class="page-card-tags">{tags_html(p['tags'][:5])}</div>
            </a>''')
        sections.append(f'''
        <section class="category-section" id="cat-{anchor_id(cat)}">
            <h2 class="category-title">
                <span class="cat-count">{len(cat_pages)}</span>
                {html.escape(cat)}
            </h2>
            <div class="page-grid compact-grid">
                {''.join(items)}
            </div>
        </section>''')

    cat_nav = ''.join(
        f'<a href="#cat-{anchor_id(cat)}" class="cat-nav-item"><span class="cat-count">{len(names)}</span>{html.escape(cat)}</a>'
        for cat, names in category_items if any(n in pages for n in names)
    )

    body = f'''
    <div class="listing-header">
        <div class="breadcrumb">
            <a href="../index.html">总览</a> <span class="sep">/</span>
            <span class="current">概念</span>
        </div>
        <h1>概念</h1>
        <p class="listing-desc">按研究主题组织的技术路线、方法和范式，共 {total} 个页面、{len(category_items)} 个分组。每张卡片保留更长摘要和主要小节。</p>
    </div>
    <div class="cat-nav">{cat_nav}</div>
    {''.join(sections)}
    '''

    return html_head('概念', 'concepts', 'concepts') + body + html_foot('concepts')


# ── Papers Listing ──────────────────────────────────────────

def generate_papers_listing(papers):
    items = []
    for p in papers:
        md_href = f"../source/raw/papers/{p['relpath']}"
        page_href = f"{p['name']}.html"
        display_title = p.get('title_zh') or p['title']
        quality = p.get('quality') or 'raw'
        type_label = p.get('paper_type') or 'paper'
        items.append(f'''
        <div class="list-item paper-item">
            <div class="list-item-main">
                <h3><a href="{page_href}" class="paper-title-link">{html.escape(display_title)}</a></h3>
                {f'<span class="paper-original-title">{html.escape(p["title"])}</span>' if display_title != p["title"] else ''}
                <p>{html.escape(p['preview'])}</p>
                <span class="paper-id">{p['arxiv_id']}</span>
            </div>
            <div class="list-item-meta">
                <span class="list-item-date">{p['created']}</span>
                <span class="paper-quality {html.escape(quality)}">{html.escape(type_label)}</span>
                <a href="{page_href}" class="md-link" title="阅读 HTML 页面">阅读</a>
                <a href="{md_href}" class="md-link" title="查看源 Markdown">源文件</a>
            </div>
        </div>''')

    body = f'''
    <div class="listing-header">
        <div class="breadcrumb">
            <a href="../index.html">总览</a> <span class="sep">/</span>
            <span class="current">论文</span>
        </div>
        <h1>论文研究卡片</h1>
        <p class="listing-desc">来自 arXiv 等来源的论文材料，共 {len(papers)} 篇。页面优先展示中文研究卡片，并保留原始 Markdown / 清洗稿入口。</p>
    </div>
    <div class="list-view">
        {''.join(items)}
    </div>
    '''

    return html_head('论文', 'papers', 'papers') + body + html_foot('papers')


def generate_paper_detail(paper, pages):
    has_brief = bool(paper.get('brief_content'))
    rendered = render_markdown(paper['brief_content'] if has_brief else paper['content'], pages)
    source_md_href = f"../source/{paper['md_relpath']}"
    source_label = paper['source'] or 'Markdown'
    clean_link = ''
    if paper.get('clean_relpath'):
        clean_link = f'''
            <a href="../source/{paper['clean_relpath']}" class="view-md-btn" title="查看清洗后的 Markdown">
                <span class="md-icon">↗</span> 清洗稿
            </a>'''
    brief_link = ''
    if paper.get('brief_relpath'):
        brief_link = f'''
            <a href="../source/{paper['brief_relpath']}" class="view-md-btn" title="查看中文卡片 Markdown">
                <span class="md-icon">↗</span> 中文卡片
            </a>'''

    external_link = ''
    if paper['url']:
        external_link = f'''
            <a href="{html.escape(paper['url'])}" class="view-md-btn" title="打开原始论文链接">
                <span class="md-icon">↗</span> 原始论文
            </a>'''

    guide_source = paper['brief_content'] if has_brief else paper['content']
    guide_items = ''.join(f'<li>{html.escape(h)}</li>' for h in get_headings(guide_source, 8))
    guide_html = f'''
            <section class="reading-guide">
                <div class="guide-kicker">论文导读</div>
                <p>{html.escape(paper['preview'] or get_preview(paper["brief_content"] if has_brief else paper["content"], 360))}</p>
                {f'<ol>{guide_items}</ol>' if guide_items else ''}
            </section>'''

    title = paper.get('title_zh') or paper['title']
    quality = paper.get('quality') or ('ok' if has_brief else 'raw')
    quality_label = {
        'ok': '中文卡片',
        'source_limited': '源材料不足',
        'pending_brief': '待中文精读',
        'raw': '原文渲染',
    }.get(str(quality), str(quality))

    body = f'''
    <div class="detail-header">
        <div class="breadcrumb">
            <a href="../index.html">总览</a> <span class="sep">/</span>
            <a href="index.html">论文</a> <span class="sep">/</span>
            <span class="current">{html.escape(title[:40])}</span>
        </div>
        <div class="detail-top-bar">
            {external_link}
            {brief_link}
            {clean_link}
            <a href="{source_md_href}" class="view-md-btn" title="查看源 Markdown">
                <span class="md-icon">↗</span> 原始源
            </a>
        </div>
    </div>

    <article class="detail-content">
        <div class="detail-meta">
            <div class="detail-type-badge papers">论文</div>
            <div class="meta-row"><span class="meta-label">arXiv</span><span class="meta-value">{html.escape(paper["arxiv_id"])}</span></div>
            <div class="meta-row"><span class="meta-label">时间</span><span class="meta-value">{html.escape(paper["created"] or "未标注")}</span></div>
            <div class="meta-row"><span class="meta-label">来源</span><span class="meta-value">{html.escape(str(source_label))}</span></div>
            <div class="meta-row"><span class="meta-label">页面质量</span><span class="meta-value">{html.escape(quality_label)}</span></div>
            <div class="meta-row"><span class="meta-label">阅读量级</span><span class="meta-value">{reading_minutes(paper["content"])} 分钟</span></div>
        </div>
        <div class="detail-body paper-detail-body">
            {f'<p class="paper-original-title-block">{html.escape(paper["title"])}</p>' if title != paper["title"] else ''}
            {guide_html}
            {rendered}
        </div>
    </article>
    '''

    return html_head(title, 'papers', 'papers') + body + html_foot('papers')


# ── Detail Page ─────────────────────────────────────────────

def source_href(source):
    source_path = str(source)
    if source_path.startswith('raw/papers/') and source_path.endswith('.md'):
        return f"../papers/{Path(source_path).stem}.html"
    return f"../source/{source_path}"


def generate_detail(page, pages, backlinks):
    rendered = render_markdown(page['content'], pages)
    bl = backlinks.get(page['name'], [])
    bl_links = []
    for bl_name in bl:
        if bl_name in pages:
            bp = pages[bl_name]
            bl_links.append(f'<a href="../{bp["type"]}/{bl_name}.html" class="backlink-item">{bp["title"]}</a>')

    source_md_href = f"../source/{page['md_relpath']}"

    meta_html = ''
    if page['created']:
        meta_html += f'<div class="meta-row"><span class="meta-label">创建</span><span class="meta-value">{format_date(page["created"])}</span></div>'
    if page['updated']:
        meta_html += f'<div class="meta-row"><span class="meta-label">更新</span><span class="meta-value">{format_date(page["updated"])}</span></div>'
    meta_html += f'<div class="meta-row"><span class="meta-label">阅读量级</span><span class="meta-value">{reading_minutes(page["content"])} 分钟</span></div>'

    sources_html = ''
    if page['sources']:
        src_items = []
        for s in page['sources']:
            src_items.append(f'<a href="{source_href(s)}" class="source-link" title="{s}">{Path(str(s)).stem}</a>')
        sources_html = f'<div class="meta-row"><span class="meta-label">来源</span><span class="meta-value sources-list">{", ".join(src_items)}</span></div>'

    guide_items = ''.join(f'<li>{html.escape(h)}</li>' for h in get_headings(page['content'], 8))
    guide_html = f'''
            <section class="reading-guide">
                <div class="guide-kicker">{TYPE_LABELS.get(page["type"], page["type"])}导读</div>
                <p>{html.escape(get_preview(page["content"], 360))}</p>
                {f'<ol>{guide_items}</ol>' if guide_items else ''}
            </section>'''

    body = f'''
    <div class="detail-header">
        <div class="breadcrumb">
            <a href="../index.html">总览</a> <span class="sep">/</span>
            <a href="index.html">{TYPE_LABELS.get(page["type"], page["type"])}</a> <span class="sep">/</span>
            <span class="current">{html.escape(page["title"][:40])}</span>
        </div>
        <div class="detail-top-bar">
            <a href="{source_md_href}" class="view-md-btn" title="查看源 Markdown">
                <span class="md-icon">↗</span> 源 Markdown
            </a>
        </div>
    </div>

    <article class="detail-content">
        <div class="detail-meta">
            <div class="detail-type-badge {page["type"]}">{TYPE_LABELS.get(page["type"], page["type"])}</div>
            <div class="detail-tags">{tags_html(page["tags"])}</div>
            {meta_html}
            {sources_html}
        </div>
        <div class="detail-body">
            {guide_html}
            {rendered}
        </div>
    </article>

    {f'  <section class="backlinks-section" id="backlinks"><h2>反向链接（{len(bl_links)}）</h2><div class="backlinks-list">{"".join(bl_links)}</div></section>' if bl_links else ''}
    '''

    return html_head(page['title'], page['type'], page['type']) + body + html_foot(page['type'])


# ── Tags Page ───────────────────────────────────────────────

def generate_tags_page(pages):
    all_tags = defaultdict(list)
    for p in pages.values():
        for t in p['tags']:
            all_tags[t].append(p)

    sections = []
    for tag, tag_pages in sorted(all_tags.items(), key=lambda x: -len(x[1])):
        color = TAG_COLORS.get(tag, DEFAULT_TAG_COLOR)
        items = []
        for p in sorted(tag_pages, key=lambda x: x['title'].lower()):
            items.append(f'<a href="{p["type"]}/{p["name"]}.html" class="tag-page-link">{p["title"]}</a>')
        sections.append(f'''
        <section class="tag-section" id="tag-{anchor_id(tag)}">
            <h2 style="--tag-color: {color}">
                <span class="tag" style="--tag-color: {color}">{tag}</span>
                <span class="tag-count">{len(tag_pages)}</span>
            </h2>
            <div class="tag-page-list">{"".join(items)}</div>
        </section>''')

    body = f'''
    <div class="listing-header">
        <div class="breadcrumb">
            <a href="index.html">总览</a> <span class="sep">/</span>
            <span class="current">标签</span>
        </div>
        <h1>标签</h1>
        <p class="listing-desc">{len(all_tags)} 个标签覆盖 {len(pages)} 个页面，用于按主题快速横向浏览。</p>
    </div>
    {''.join(sections)}
    '''

    return html_head('标签', 'home') + body + html_foot()


# ═══════════════════════════════════════════════════════════════
# Search Index
# ═══════════════════════════════════════════════════════════════

def generate_search_index(pages, papers=None):
    entries = []
    for p in pages.values():
        entries.append({
            'name': p['name'],
            'title': p['title'],
            'type': p['type'],
            'typeLabel': TYPE_LABELS.get(p['type'], p['type']),
            'tags': p['tags'],
            'preview': get_preview(p['content'], 240),
            'href': f"{p['type']}/{p['name']}.html",
        })
    for p in papers or []:
        paper_title = p.get('title_zh') or p['title']
        paper_preview = p['preview'] or get_preview(p.get('brief_content') or p['content'], 240)
        entries.append({
            'name': p['name'],
            'title': paper_title,
            'type': 'papers',
            'typeLabel': TYPE_LABELS['papers'],
            'tags': p['tags'],
            'preview': paper_preview,
            'href': f"papers/{p['name']}.html",
        })
    return json.dumps(entries, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# Static Assets
# ═══════════════════════════════════════════════════════════════

CSS = r'''
/* ═══════════════════════════════════════════════════════════════════
   LLM Wiki — "Scholar's Ink" Theme
   A dark, editorial knowledge base inspired by research journals,
   illuminated manuscripts, and the texture of fine ink on paper.
   ═══════════════════════════════════════════════════════════════════ */

:root {
    --bg-deep: #08090C;
    --bg-primary: #0C0E13;
    --bg-secondary: #111318;
    --bg-surface: #171A22;
    --bg-elevated: #1D2029;
    --bg-glass: rgba(23, 26, 34, 0.75);

    --ink-primary: #D8D3CA;
    --ink-secondary: #A09B90;
    --ink-faded: #5C5850;
    --ink-ghost: #3A3733;

    --gold: #C8956C;
    --gold-bright: #E4B07C;
    --gold-dim: rgba(200, 149, 108, 0.10);
    --gold-glow: rgba(200, 149, 108, 0.06);

    --teal: #5DAE96;
    --teal-dim: rgba(93, 174, 150, 0.10);

    --slate-blue: #7A9BBF;
    --slate-blue-dim: rgba(122, 155, 191, 0.10);

    --rose: #BF6A7A;
    --rose-dim: rgba(191, 106, 122, 0.10);

    --border: rgba(200, 195, 185, 0.07);
    --border-hover: rgba(200, 195, 185, 0.14);

    --radius-xs: 4px;
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 20px;
    --radius-xl: 28px;

    --font-display: 'Fraunces', 'Noto Sans SC', serif;
    --font-body: 'EB Garamond', 'Noto Sans SC', Georgia, serif;
    --font-sans: 'Noto Sans SC', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

    --sidebar-w: 272px;
    --content-w: 880px;

    --transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 17px; scroll-behavior: smooth; }

body {
    font-family: var(--font-body);
    background: var(--bg-deep);
    color: var(--ink-primary);
    line-height: 1.75;
    display: flex;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Subtle grain texture overlay */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

a {
    color: var(--slate-blue);
    text-decoration: none;
    transition: color var(--transition);
}
a:hover { color: var(--gold-bright); }

::selection {
    background: rgba(200, 149, 108, 0.25);
    color: var(--ink-primary);
}

/* ══════════════════════════════════════════════════════════════
   Sidebar — The Window
   ══════════════════════════════════════════════════════════════ */

#sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--sidebar-w);
    height: 100vh;
    background: var(--bg-primary);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    z-index: 100;
    overflow-y: auto;
    overflow-x: hidden;
}

/* Soft glow at top of sidebar */
#sidebar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(ellipse at 30% 0%, var(--gold-glow) 0%, transparent 70%);
    pointer-events: none;
}

.sidebar-header {
    position: relative;
    padding: 36px 28px 28px;
    border-bottom: 1px solid var(--border);
}

.site-title {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
}

.title-icon {
    font-size: 1.4rem;
    color: var(--gold);
    line-height: 1;
}

.title-text {
    font-family: var(--font-display);
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--ink-primary);
    letter-spacing: 0.01em;
    font-optical-sizing: auto;
}

.site-subtitle {
    font-family: var(--font-sans);
    font-size: 0.68rem;
    color: var(--ink-faded);
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 400;
    padding-left: 32px;
}

.sidebar-nav {
    position: relative;
    padding: 20px 14px;
    display: flex;
    flex-direction: column;
    gap: 1px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 16px;
    border-radius: var(--radius-sm);
    color: var(--ink-secondary);
    font-family: var(--font-sans);
    font-size: 0.84rem;
    font-weight: 500;
    transition: all var(--transition);
    position: relative;
}

.nav-item:hover {
    background: var(--bg-surface);
    color: var(--ink-primary);
}

.nav-item.active {
    background: var(--gold-dim);
    color: var(--gold);
    font-weight: 600;
}

.nav-item.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 6px;
    bottom: 6px;
    width: 3px;
    border-radius: 0 2px 2px 0;
    background: var(--gold);
}

.nav-icon {
    font-size: 1rem;
    width: 20px;
    text-align: center;
    opacity: 0.6;
}

.nav-item.active .nav-icon { opacity: 1; }

.sidebar-footer {
    margin-top: auto;
    border-top: 1px solid var(--border);
    padding: 16px;
}

.sidebar-search { position: relative; }

.search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: 12px;
    color: var(--ink-faded);
    pointer-events: none;
    flex-shrink: 0;
}

#search-input {
    width: 100%;
    padding: 10px 12px 10px 36px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--ink-primary);
    font-family: var(--font-sans);
    font-size: 0.82rem;
    outline: none;
    transition: all var(--transition);
}

#search-input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 0 3px var(--gold-dim);
}

#search-input::placeholder { color: var(--ink-faded); }

.search-results {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    right: 0;
    max-height: 55vh;
    overflow-y: auto;
    background: var(--bg-elevated);
    border: 1px solid var(--border-hover);
    border-radius: var(--radius-md);
    box-shadow: 0 -16px 48px rgba(0, 0, 0, 0.5);
    display: none;
    z-index: 200;
}

.search-results.visible { display: block; }

.search-result-item {
    display: block;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
    text-decoration: none;
}

.search-result-item:last-child { border-bottom: none; }
.search-result-item:hover { background: var(--bg-surface); }

.search-result-item .sr-title {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--ink-primary);
}

.search-result-item mark {
    background: rgba(200, 149, 108, 0.3);
    color: var(--gold-bright);
    border-radius: 2px;
    padding: 0 2px;
}

.search-result-item .sr-type {
    font-family: var(--font-sans);
    font-size: 0.62rem;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-left: 8px;
    font-weight: 600;
}

.search-result-item .sr-preview {
    font-size: 0.78rem;
    color: var(--ink-faded);
    margin-top: 3px;
    line-height: 1.5;
}

/* ══════════════════════════════════════════════════════════════
   Mobile Toggle
   ══════════════════════════════════════════════════════════════ */

#sidebar-toggle {
    display: none;
    position: fixed;
    top: 16px;
    left: 16px;
    z-index: 200;
    width: 40px;
    height: 40px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    cursor: pointer;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
}

#sidebar-toggle span {
    display: block;
    width: 18px;
    height: 2px;
    background: var(--ink-secondary);
    border-radius: 1px;
    transition: all var(--transition);
}

/* ══════════════════════════════════════════════════════════════
   Main Content
   ══════════════════════════════════════════════════════════════ */

#main {
    margin-left: var(--sidebar-w);
    flex: 1;
    padding: 48px 56px 100px;
    max-width: calc(var(--sidebar-w) + var(--content-w) + 112px);
    min-width: 0;
    position: relative;
    animation: pageIn 0.5s ease-out;
}

@keyframes pageIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ══════════════════════════════════════════════════════════════
   Breadcrumb
   ══════════════════════════════════════════════════════════════ */

.breadcrumb {
    font-family: var(--font-sans);
    font-size: 0.76rem;
    color: var(--ink-faded);
    margin-bottom: 24px;
    letter-spacing: 0.02em;
}

.breadcrumb a { color: var(--ink-faded); }
.breadcrumb a:hover { color: var(--gold); }
.breadcrumb .sep { margin: 0 8px; opacity: 0.3; }
.breadcrumb .current { color: var(--ink-secondary); }

/* ══════════════════════════════════════════════════════════════
   Home Page
   ══════════════════════════════════════════════════════════════ */

.home-header {
    margin-bottom: 48px;
    padding-bottom: 40px;
    border-bottom: 1px solid var(--border);
}

.home-title {
    font-family: var(--font-display);
    font-size: 3.2rem;
    font-weight: 800;
    color: var(--ink-primary);
    margin-bottom: 12px;
    line-height: 1.05;
    letter-spacing: -0.02em;
}

.home-desc {
    font-family: var(--font-sans);
    font-size: 0.92rem;
    color: var(--ink-secondary);
    line-height: 1.7;
    max-width: 540px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 56px;
}

.stat-card {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 28px 20px 24px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    transition: all var(--transition);
    text-decoration: none;
    overflow: hidden;
}

.stat-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius-lg);
    background: radial-gradient(ellipse at 50% 0%, var(--gold-glow) 0%, transparent 60%);
    opacity: 0;
    transition: opacity var(--transition);
}

.stat-card:hover {
    border-color: var(--gold);
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(200, 149, 108, 0.08);
}

.stat-card:hover::after { opacity: 1; }

.stat-icon {
    font-size: 1.4rem;
    margin-bottom: 10px;
    opacity: 0.5;
    position: relative;
    z-index: 1;
}

.stat-number {
    font-family: var(--font-display);
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--gold);
    line-height: 1;
    position: relative;
    z-index: 1;
}

.stat-label {
    font-family: var(--font-sans);
    font-size: 0.72rem;
    color: var(--ink-faded);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 8px;
    position: relative;
    z-index: 1;
}

.home-grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 40px;
}

.section-title {
    font-family: var(--font-display);
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--ink-primary);
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    letter-spacing: -0.01em;
}

.recent-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
}

.recent-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    transition: background 0.15s;
    text-decoration: none;
}

.recent-item:hover { background: var(--bg-surface); }

.recent-type {
    font-family: var(--font-sans);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border-radius: 3px;
    font-weight: 600;
    min-width: 64px;
    text-align: center;
    flex-shrink: 0;
}

.recent-type.entities { background: var(--gold-dim); color: var(--gold); }
.recent-type.concepts { background: var(--teal-dim); color: var(--teal); }
.recent-type.queries { background: var(--slate-blue-dim); color: var(--slate-blue); }

.recent-title {
    flex: 1;
    font-size: 0.92rem;
    color: var(--ink-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.recent-date {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--ink-faded);
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════════════
   Tag Cloud
   ══════════════════════════════════════════════════════════════ */

.tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    align-items: center;
}

.tag {
    font-family: var(--font-sans);
    display: inline-block;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 500;
    background: color-mix(in srgb, var(--tag-color, #888) 10%, transparent);
    color: var(--tag-color, #888);
    border: 1px solid color-mix(in srgb, var(--tag-color, #888) 16%, transparent);
    transition: all var(--transition);
    white-space: nowrap;
}

.tag:hover {
    background: color-mix(in srgb, var(--tag-color, #888) 20%, transparent);
    border-color: color-mix(in srgb, var(--tag-color, #888) 50%, transparent);
    transform: translateY(-1px);
}

.tag small { opacity: 0.5; font-size: 0.7em; }

/* ══════════════════════════════════════════════════════════════
   Page Grid — Entity / Concept Cards
   ══════════════════════════════════════════════════════════════ */

.page-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 14px;
}

.page-grid.compact-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 10px;
}

.page-card {
    display: flex;
    flex-direction: column;
    padding: 22px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: all var(--transition);
    text-decoration: none;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.page-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--gold), var(--teal));
    opacity: 0;
    transition: opacity var(--transition);
}

.page-card:hover {
    border-color: var(--border-hover);
    background: var(--bg-elevated);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.page-card:hover::before { opacity: 1; }

.page-card.compact { padding: 16px 18px; }

.page-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.page-card-title {
    font-family: var(--font-body);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ink-primary);
    line-height: 1.3;
}

.page-card-date {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--ink-faded);
    white-space: nowrap;
    margin-left: 12px;
    padding-top: 3px;
}

.page-card-preview {
    font-size: 0.86rem;
    color: var(--ink-secondary);
    line-height: 1.55;
    flex: 1;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.page-card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

/* ══════════════════════════════════════════════════════════════
   List View — Queries / Papers
   ══════════════════════════════════════════════════════════════ */

.list-view {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: all var(--transition);
    text-decoration: none;
}

.list-item:hover {
    border-color: var(--border-hover);
    background: var(--bg-elevated);
    transform: translateX(4px);
}

.list-item h3 {
    font-family: var(--font-body);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--ink-primary);
    margin-bottom: 4px;
}

.list-item p {
    font-size: 0.84rem;
    color: var(--ink-faded);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.list-item-date {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--ink-faded);
}

.list-item-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
    text-align: right;
    flex-shrink: 0;
    margin-left: 24px;
}

/* ══════════════════════════════════════════════════════════════
   Papers
   ══════════════════════════════════════════════════════════════ */

.paper-item .paper-id {
    font-family: var(--font-mono);
    font-size: 0.76rem;
    color: var(--ink-faded);
}

.paper-title-link {
    color: inherit;
    text-decoration: none;
}

.paper-title-link:hover {
    color: var(--gold-bright);
}

.paper-original-title,
.paper-original-title-block {
    display: block;
    font-family: var(--font-body);
    color: var(--ink-faded);
}

.paper-original-title {
    font-size: 0.78rem;
    margin-bottom: 6px;
}

.paper-original-title-block {
    font-size: 0.9rem;
    margin-bottom: 20px;
}

.paper-quality {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    max-width: 120px;
    padding: 3px 8px;
    background: var(--teal-dim);
    border: 1px solid color-mix(in srgb, var(--teal) 22%, transparent);
    border-radius: var(--radius-xs);
    color: var(--teal);
    font-family: var(--font-mono);
    font-size: 0.68rem;
}

.paper-quality.source_limited {
    background: var(--gold-dim);
    border-color: color-mix(in srgb, var(--gold) 22%, transparent);
    color: var(--gold);
}

.paper-quality.pending_brief {
    background: var(--slate-blue-dim);
    border-color: color-mix(in srgb, var(--slate-blue) 22%, transparent);
    color: var(--slate-blue);
}

.md-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 10px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xs);
    color: var(--gold);
    font-family: var(--font-mono);
    font-size: 0.74rem;
    transition: all var(--transition);
}

.md-link:hover {
    border-color: var(--gold);
    background: var(--gold-dim);
}

/* ══════════════════════════════════════════════════════════════
   Category Navigation — Concepts
   ══════════════════════════════════════════════════════════════ */

.cat-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 40px;
    padding: 18px;
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
}

.cat-nav-item {
    font-family: var(--font-sans);
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    color: var(--ink-secondary);
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    transition: all var(--transition);
}

.cat-nav-item:hover {
    color: var(--gold);
    border-color: var(--gold);
    background: var(--gold-dim);
}

.cat-nav-item .cat-count {
    font-size: 0.64rem;
    font-weight: 700;
    color: var(--gold);
}

.category-section {
    margin-bottom: 48px;
    animation: pageIn 0.4s ease-out both;
}

.category-title {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink-primary);
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    letter-spacing: -0.01em;
}

.category-title .cat-count {
    font-family: var(--font-sans);
    font-size: 0.68rem;
    background: var(--gold-dim);
    color: var(--gold);
    padding: 2px 9px;
    border-radius: 10px;
    font-weight: 600;
}

/* ══════════════════════════════════════════════════════════════
   Detail Page — The Reading Room
   ══════════════════════════════════════════════════════════════ */

.detail-header { margin-bottom: 36px; }

.detail-top-bar {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.view-md-btn {
    font-family: var(--font-sans);
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 16px;
    background: var(--gold-dim);
    border: 1px solid color-mix(in srgb, var(--gold) 24%, transparent);
    border-radius: var(--radius-sm);
    color: var(--gold);
    font-size: 0.78rem;
    font-weight: 500;
    transition: all var(--transition);
}

.view-md-btn:hover {
    background: color-mix(in srgb, var(--gold) 18%, transparent);
    border-color: var(--gold);
    color: var(--gold-bright);
}

.md-icon { font-size: 0.85rem; }

.detail-content {
    display: grid;
    grid-template-columns: 210px 1fr;
    gap: 36px;
}

.detail-meta {
    position: sticky;
    top: 40px;
    align-self: start;
    padding: 20px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}

.detail-type-badge {
    font-family: var(--font-sans);
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 14px;
}

.detail-type-badge.entities { background: var(--gold-dim); color: var(--gold); }
.detail-type-badge.concepts { background: var(--teal-dim); color: var(--teal); }
.detail-type-badge.queries { background: var(--slate-blue-dim); color: var(--slate-blue); }
.detail-type-badge.papers { background: var(--gold-dim); color: var(--gold-bright); }

.detail-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 18px;
}

.meta-row {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-bottom: 12px;
}

.meta-label {
    font-family: var(--font-sans);
    color: var(--ink-faded);
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.meta-value {
    font-family: var(--font-mono);
    color: var(--ink-secondary);
    font-size: 0.76rem;
}

.sources-list {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.source-link {
    font-size: 0.72rem;
    color: var(--slate-blue);
}

.detail-body { min-width: 0; }

.detail-body h1 {
    font-family: var(--font-display);
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 28px;
    line-height: 1.15;
    color: var(--ink-primary);
    letter-spacing: -0.02em;
}

.detail-body h2 {
    font-family: var(--font-display);
    font-size: 1.45rem;
    font-weight: 600;
    margin-top: 44px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    color: var(--ink-primary);
    letter-spacing: -0.01em;
}

.detail-body h3 {
    font-family: var(--font-body);
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 28px;
    margin-bottom: 10px;
    color: var(--ink-primary);
}

.detail-body p {
    margin-bottom: 16px;
    line-height: 1.85;
    color: color-mix(in srgb, var(--ink-primary) 90%, transparent);
}

.detail-body ul, .detail-body ol {
    margin-bottom: 16px;
    padding-left: 28px;
}

.detail-body li {
    margin-bottom: 6px;
    line-height: 1.7;
}

.detail-body li::marker { color: var(--ink-faded); }

.detail-body blockquote {
    border-left: 3px solid var(--gold);
    padding: 14px 24px;
    margin: 20px 0;
    background: color-mix(in srgb, var(--gold) 3%, transparent);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    color: var(--ink-secondary);
    font-style: italic;
}

.detail-body code {
    font-family: var(--font-mono);
    font-size: 0.82em;
    padding: 2px 7px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 3px;
    color: var(--gold);
}

.detail-body pre {
    margin: 20px 0;
    padding: 20px 24px;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow-x: auto;
    font-size: 0.82rem;
    line-height: 1.65;
}

.detail-body pre code {
    padding: 0;
    background: none;
    border: none;
    color: var(--ink-primary);
}

.detail-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 0.88rem;
}

.detail-body th, .detail-body td {
    padding: 12px 16px;
    border: 1px solid var(--border);
    text-align: left;
}

.detail-body th {
    background: var(--bg-surface);
    font-family: var(--font-sans);
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--ink-primary);
    letter-spacing: 0.02em;
}

.detail-body td { color: var(--ink-secondary); }

.detail-body tr:hover td { background: var(--bg-surface); }

.detail-body strong {
    color: var(--ink-primary);
    font-weight: 600;
}

/* ══════════════════════════════════════════════════════════════
   Wikilinks — The Threads
   ══════════════════════════════════════════════════════════════ */

.wikilink {
    color: var(--teal);
    border-bottom: 1px solid color-mix(in srgb, var(--teal) 30%, transparent);
    transition: all var(--transition);
    padding: 0 1px;
}

.wikilink:hover {
    color: #7CC9AE;
    border-bottom-color: var(--teal);
    background: var(--teal-dim);
    border-radius: 2px;
}

.wikilink.broken {
    color: var(--rose);
    border-bottom: 1px dotted var(--rose);
    opacity: 0.65;
    cursor: help;
}

/* ══════════════════════════════════════════════════════════════
   Backlinks — The Web
   ══════════════════════════════════════════════════════════════ */

.backlinks-section {
    margin-top: 56px;
    padding-top: 28px;
    border-top: 1px solid var(--border);
}

.backlinks-section h2 {
    font-family: var(--font-display);
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 14px;
    color: var(--ink-secondary);
}

.backlinks-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.backlink-item {
    display: inline-block;
    padding: 7px 16px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--ink-secondary);
    font-family: var(--font-body);
    font-size: 0.88rem;
    transition: all var(--transition);
}

.backlink-item:hover {
    border-color: var(--teal);
    color: var(--teal);
    background: var(--teal-dim);
    transform: translateY(-1px);
}

/* ══════════════════════════════════════════════════════════════
   Tags Page
   ══════════════════════════════════════════════════════════════ */

.tag-section {
    margin-bottom: 36px;
}

.tag-section h2 {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.tag-count {
    font-family: var(--font-sans);
    font-size: 0.7rem;
    color: var(--ink-faded);
}

.tag-page-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.tag-page-link {
    font-family: var(--font-sans);
    padding: 5px 14px;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--ink-secondary);
    font-size: 0.82rem;
    transition: all var(--transition);
}

.tag-page-link:hover {
    border-color: var(--gold);
    color: var(--gold);
    background: var(--gold-dim);
}

/* ══════════════════════════════════════════════════════════════
   Listing Header
   ══════════════════════════════════════════════════════════════ */

.listing-header { margin-bottom: 36px; }

.listing-header h1 {
    font-family: var(--font-display);
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 10px;
    letter-spacing: -0.02em;
}

.listing-desc {
    font-family: var(--font-sans);
    color: var(--ink-secondary);
    font-size: 0.9rem;
}

/* ══════════════════════════════════════════════════════════════
   Responsive
   ══════════════════════════════════════════════════════════════ */

@media (max-width: 900px) {
    #sidebar {
        transform: translateX(-100%);
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    #sidebar.open { transform: translateX(0); }

    #sidebar-toggle { display: flex; }

    #main {
        margin-left: 0;
        padding: 24px 20px 80px;
    }

    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .home-grid { grid-template-columns: 1fr; }
    .detail-content { grid-template-columns: 1fr; }
    .detail-meta { position: static; order: -1; }
}

@media (max-width: 600px) {
    html { font-size: 15px; }

    .stats-grid {
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }

    .page-grid { grid-template-columns: 1fr; }

    .list-item {
        flex-direction: column;
        align-items: flex-start;
    }

    .list-item-meta {
        margin-left: 0;
        margin-top: 10px;
        text-align: left;
    }
}

/* ══════════════════════════════════════════════════════════════
   Chinese Research Desk Refresh
   ══════════════════════════════════════════════════════════════ */

:root {
    --bg-deep: #EEF2F4;
    --bg-primary: #F9FAF8;
    --bg-secondary: #F3F6F7;
    --bg-surface: #FFFFFF;
    --bg-elevated: #F7FAFB;
    --bg-glass: rgba(255, 255, 255, 0.88);

    --ink-primary: #18202B;
    --ink-secondary: #4B596A;
    --ink-faded: #7A8794;
    --ink-ghost: #C9D0D7;

    --gold: #A0632D;
    --gold-bright: #C17C3A;
    --gold-dim: rgba(160, 99, 45, 0.10);
    --gold-glow: rgba(160, 99, 45, 0.06);

    --teal: #1F7A68;
    --teal-dim: rgba(31, 122, 104, 0.10);
    --slate-blue: #335C9B;
    --slate-blue-dim: rgba(51, 92, 155, 0.10);
    --rose: #B84A5A;
    --rose-dim: rgba(184, 74, 90, 0.10);

    --border: rgba(26, 36, 49, 0.10);
    --border-hover: rgba(26, 36, 49, 0.20);

    --radius-xs: 4px;
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 8px;
    --radius-xl: 8px;

    --font-display: 'Noto Sans SC', 'Fraunces', system-ui, sans-serif;
    --font-body: 'Noto Sans SC', 'EB Garamond', system-ui, sans-serif;
    --content-w: 1120px;
}

body {
    background:
        linear-gradient(90deg, rgba(51, 92, 155, 0.04), transparent 32%),
        linear-gradient(180deg, #F7F8F5 0%, #EEF2F4 100%);
    color: var(--ink-primary);
}

body::before {
    opacity: 0.035;
    mix-blend-mode: multiply;
}

#sidebar {
    background: rgba(249, 250, 248, 0.94);
    border-right: 1px solid rgba(26, 36, 49, 0.12);
    box-shadow: 12px 0 36px rgba(28, 38, 55, 0.06);
    backdrop-filter: blur(16px);
}

#sidebar::before { display: none; }

.sidebar-header {
    padding: 30px 24px 24px;
    background: linear-gradient(180deg, rgba(51, 92, 155, 0.07), transparent);
}

.title-text {
    font-size: 1.14rem;
    letter-spacing: 0;
}

.site-subtitle {
    padding-left: 0;
    letter-spacing: 0;
    text-transform: none;
    line-height: 1.5;
}

.nav-item {
    border: 1px solid transparent;
}

.nav-item:hover,
.nav-item.active {
    background: #FFFFFF;
    border-color: var(--border);
    box-shadow: 0 8px 22px rgba(28, 38, 55, 0.07);
}

#search-input {
    background: #FFFFFF;
    border-color: rgba(26, 36, 49, 0.14);
}

.search-results {
    background: #FFFFFF;
    box-shadow: 0 -18px 42px rgba(28, 38, 55, 0.16);
}

#main {
    max-width: calc(var(--sidebar-w) + var(--content-w) + 96px);
    padding: 44px 48px 96px;
}

.home-header,
.listing-header {
    background: rgba(255, 255, 255, 0.62);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    margin-bottom: 28px;
    box-shadow: 0 14px 34px rgba(28, 38, 55, 0.06);
}

.home-title,
.listing-header h1 {
    font-size: 2.45rem;
    letter-spacing: 0;
}

.home-desc,
.listing-desc {
    max-width: 820px;
    color: var(--ink-secondary);
}

.stats-grid {
    margin-bottom: 34px;
}

.stat-card,
.page-card,
.list-item,
.cat-nav,
.detail-meta,
.reading-guide,
.tag-page-link {
    background: var(--bg-surface);
    border-color: var(--border);
    box-shadow: 0 8px 24px rgba(28, 38, 55, 0.055);
}

.stat-card:hover,
.page-card:hover,
.list-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 38px rgba(28, 38, 55, 0.12);
}

.home-grid {
    grid-template-columns: minmax(0, 1.45fr) minmax(300px, 0.85fr);
    gap: 28px;
}

.section-title.secondary {
    margin-top: 26px;
}

.focus-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}

.focus-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 10px 12px;
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--ink-secondary);
    font-family: var(--font-sans);
    font-size: 0.82rem;
}

.focus-item strong {
    color: var(--slate-blue);
    font-family: var(--font-mono);
}

.recent-item {
    align-items: flex-start;
    padding: 16px 0;
    border-bottom: 1px solid var(--border);
    border-radius: 0;
}

.recent-item:hover {
    background: transparent;
}

.recent-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.recent-title {
    white-space: normal;
    font-weight: 600;
    line-height: 1.35;
}

.recent-preview {
    color: var(--ink-secondary);
    font-size: 0.82rem;
    line-height: 1.6;
}

.summary-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 2px;
}

.summary-chip {
    display: inline-flex;
    align-items: center;
    max-width: 100%;
    padding: 3px 8px;
    border-radius: var(--radius-xs);
    background: var(--slate-blue-dim);
    color: var(--slate-blue);
    font-family: var(--font-sans);
    font-size: 0.68rem;
    line-height: 1.35;
}

.page-card {
    padding: 20px;
}

.page-card-header.compact {
    margin-bottom: 8px;
}

.page-card-header.compact h3 {
    color: var(--ink-primary);
    font-size: 1rem;
    line-height: 1.35;
}

.page-card-header.compact span {
    color: var(--ink-faded);
    font-family: var(--font-mono);
    font-size: 0.66rem;
    white-space: nowrap;
}

.page-card-preview,
.list-item p,
.page-card.compact p {
    color: var(--ink-secondary);
    -webkit-line-clamp: 4;
}

.list-item {
    align-items: flex-start;
}

.list-item-main {
    min-width: 0;
}

.list-item-type {
    display: inline-flex;
    margin-bottom: 8px;
    padding: 3px 8px;
    border-radius: var(--radius-xs);
    font-family: var(--font-sans);
    font-size: 0.66rem;
    font-weight: 700;
}

.list-item-type.entities { background: var(--gold-dim); color: var(--gold); }
.list-item-type.concepts { background: var(--teal-dim); color: var(--teal); }
.list-item-type.queries { background: var(--slate-blue-dim); color: var(--slate-blue); }

.cat-nav {
    position: sticky;
    top: 0;
    z-index: 4;
    backdrop-filter: blur(16px);
}

.cat-nav-item {
    border-radius: var(--radius-xs);
    background: #FFFFFF;
}

.category-section {
    scroll-margin-top: 90px;
}

.detail-header {
    margin-bottom: 22px;
}

.detail-content {
    grid-template-columns: 240px minmax(0, 1fr);
}

.detail-meta {
    top: 24px;
}

.detail-body {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 34px 42px;
    box-shadow: 0 16px 40px rgba(28, 38, 55, 0.07);
}

.reading-guide {
    padding: 18px 20px;
    margin-bottom: 30px;
    border-left: 4px solid var(--slate-blue);
}

.guide-kicker {
    font-family: var(--font-sans);
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--slate-blue);
    margin-bottom: 8px;
}

.reading-guide p {
    color: var(--ink-secondary);
    margin-bottom: 12px;
}

.reading-guide ol {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px 18px;
    margin: 0;
    padding-left: 20px;
}

.reading-guide li {
    color: var(--ink-secondary);
    font-size: 0.86rem;
    margin-bottom: 0;
}

.detail-body h1 {
    font-size: 2rem;
    letter-spacing: 0;
}

.detail-body h2 {
    letter-spacing: 0;
    border-bottom-color: rgba(51, 92, 155, 0.16);
}

.detail-body pre {
    background: #172033;
}

.detail-body pre code {
    color: #EEF2F4;
}

.detail-body table {
    background: #FFFFFF;
}

.backlinks-section {
    margin-left: 276px;
}

@media (max-width: 900px) {
    .home-grid,
    .detail-content {
        grid-template-columns: 1fr;
    }
    .detail-body {
        padding: 26px 22px;
    }
    .backlinks-section {
        margin-left: 0;
    }
    .cat-nav {
        position: static;
    }
}

@media (max-width: 600px) {
    #main {
        padding: 72px 16px 72px;
    }
    .home-header,
    .listing-header {
        padding: 22px 18px;
    }
    .home-title,
    .listing-header h1 {
        font-size: 1.9rem;
    }
    .focus-grid,
    .reading-guide ol {
        grid-template-columns: 1fr;
    }
    .recent-date {
        display: none;
    }
}

/* ══════════════════════════════════════════════════════════════
   Scrollbar
   ══════════════════════════════════════════════════════════════ */

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--ink-ghost);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--ink-faded); }
'''

JS = r'''
/* ═══════════════════════════════════════════════════════════════════
   LLM Wiki — "Scholar's Ink" Interactivity
   ═══════════════════════════════════════════════════════════════════ */

(function() {
    'use strict';

    // ── Page Load Animation ───────────────────────────────
    function staggerReveal() {
        var main = document.getElementById('main');
        if (!main) return;
        var els = main.querySelectorAll(
            '.stat-card, .page-card, .list-item, .category-section, .recent-item, .cat-nav-item, .tag-section'
        );
        for (var i = 0; i < els.length; i++) {
            els[i].style.opacity = '0';
            els[i].style.transform = 'translateY(12px)';
            els[i].style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            els[i].style.transitionDelay = Math.min(i * 40, 600) + 'ms';
        }
        requestAnimationFrame(function() {
            requestAnimationFrame(function() {
                for (var i = 0; i < els.length; i++) {
                    els[i].style.opacity = '1';
                    els[i].style.transform = 'translateY(0)';
                }
            });
        });
    }

    // ── Sidebar Toggle (mobile) ───────────────────────────
    var toggle = document.getElementById('sidebar-toggle');
    var sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            var spans = toggle.querySelectorAll('span');
            if (sidebar.classList.contains('open')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                spans[0].style.transform = '';
                spans[1].style.opacity = '';
                spans[2].style.transform = '';
            }
        });
    }

    // ── Search ────────────────────────────────────────────
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    var searchData = null;
    var debounceTimer = null;

    function getRoot() {
        if (typeof window.WIKI_ROOT === 'string') return window.WIKI_ROOT;
        var path = window.location.pathname;
        var depth = (path.match(/\//g) || []).length - 1;
        if (depth <= 2) return './';
        return '../'.repeat(depth - 2);
    }

    function loadSearchData() {
        if (searchData) return Promise.resolve(searchData);
        return fetch(getRoot() + 'search-index.json')
            .then(function(r) { return r.json(); })
            .then(function(d) { searchData = d; return d; })
            .catch(function(e) { console.warn('Search index load failed:', e); return []; });
    }

    function hl(text, q) {
        if (!q) return text;
        var e = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp('(' + e + ')', 'gi'), '<mark>$1</mark>');
    }

    function doSearch(query) {
        if (!query || query.length < 2) { results.classList.remove('visible'); return; }
        loadSearchData().then(function(data) {
            var lower = query.toLowerCase();
            var scored = data.map(function(entry) {
                var s = 0;
                if (entry.title.toLowerCase().indexOf(lower) >= 0) s += 10;
                if (entry.name.toLowerCase().indexOf(lower) >= 0) s += 8;
                entry.tags.forEach(function(t) { if (t.toLowerCase().indexOf(lower) >= 0) s += 5; });
                if (entry.preview.toLowerCase().indexOf(lower) >= 0) s += 2;
                return { name: entry.name, title: entry.title, type: entry.type, typeLabel: entry.typeLabel || entry.type, href: entry.href, preview: entry.preview, score: s };
            }).filter(function(e) { return e.score > 0; }).sort(function(a,b) { return b.score - a.score; }).slice(0, 12);

            if (!scored.length) {
                results.innerHTML = '<div class="search-result-item"><span class="sr-preview">没有找到匹配内容</span></div>';
            } else {
                var root = getRoot();
                results.innerHTML = scored.map(function(e) {
                    return '<a href="' + root + e.href + '" class="search-result-item"><div><span class="sr-title">' + hl(e.title, query) + '</span><span class="sr-type">' + e.typeLabel + '</span></div><div class="sr-preview">' + hl(e.preview.substring(0, 120), query) + '</div></a>';
                }).join('');
            }
            results.classList.add('visible');
        });
    }

    if (input) {
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() { doSearch(input.value.trim()); }, 200);
        });
        input.addEventListener('focus', function() {
            if (input.value.trim().length >= 2) doSearch(input.value.trim());
        });
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.sidebar-search')) results.classList.remove('visible');
        });
        document.addEventListener('keydown', function(e) {
            if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
            if (e.key === 'Escape') { results.classList.remove('visible'); input.blur(); }
        });
    }

    // ── Smooth scroll ─────────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(function(a) {
        a.addEventListener('click', function(e) {
            var t = document.querySelector(a.getAttribute('href'));
            if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });

    // ── Scroll progress bar (detail pages) ────────────────
    var mainEl = document.getElementById('main');
    if (mainEl && document.querySelector('.detail-content')) {
        var bar = document.createElement('div');
        bar.id = 'scroll-progress';
        bar.style.cssText = 'position:fixed;top:0;left:var(--sidebar-w);right:0;height:2px;background:linear-gradient(90deg,var(--gold),var(--teal));z-index:999;transform-origin:left;transform:scaleX(0);transition:transform 0.1s';
        document.body.appendChild(bar);
        window.addEventListener('scroll', function() {
            var h = document.documentElement.scrollHeight - window.innerHeight;
            bar.style.transform = 'scaleX(' + (h > 0 ? window.scrollY / h : 0) + ')';
        }, { passive: true });
    }

    // ── Init ──────────────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', staggerReveal);
    } else {
        staggerReveal();
    }
})();'''


# ═══════════════════════════════════════════════════════════════
# Main Generation
# ═══════════════════════════════════════════════════════════════

def generate_all():
    print("Loading wiki pages...")
    pages = load_all_pages()
    print(f"  Found {len(pages)} pages")

    print("Loading paper sources...")
    papers = load_all_papers()
    print(f"  Found {len(papers)} papers")

    print("Building backlink index...")
    backlinks = build_backlinks(pages)

    print("Building concept categories...")
    categories = build_concept_categories(pages)
    print(f"  Found {len(categories)} categories")

    # Clean output directory (skip symlinks)
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.is_symlink():
                f.unlink()
            elif f.is_dir() and f.name not in ('static', 'source'):
                import shutil
                shutil.rmtree(f)
            elif f.is_file():
                f.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create source symlinks for MD file access
    source_dir = OUTPUT_DIR / 'source'
    source_dir.mkdir(exist_ok=True)
    for target in ['entities', 'concepts', 'queries', 'raw', 'papers', 'paper-briefs', 'references']:
        link = source_dir / target
        if (WIKI_ROOT / target).exists() and not link.exists():
            link.symlink_to(WIKI_ROOT / target)

    # Create static dir
    static_dir = OUTPUT_DIR / 'static'
    static_dir.mkdir(exist_ok=True)
    (static_dir / 'wiki.css').write_text(CSS, encoding='utf-8')
    (static_dir / 'wiki.js').write_text(JS, encoding='utf-8')
    print("  Wrote static assets")

    # Generate search index
    (OUTPUT_DIR / 'search-index.json').write_text(generate_search_index(pages, papers), encoding='utf-8')
    print("  Wrote search index")

    # Home page
    (OUTPUT_DIR / 'index.html').write_text(generate_home(pages, backlinks, categories), encoding='utf-8')
    print("  Generated home page")

    # Tags page
    (OUTPUT_DIR / 'tags.html').write_text(generate_tags_page(pages), encoding='utf-8')

    # Entity listing
    ent_dir = OUTPUT_DIR / 'entities'
    ent_dir.mkdir(exist_ok=True)
    (ent_dir / 'index.html').write_text(
        generate_listing(pages, 'entities', '实体', TYPE_DESCRIPTIONS['entities'], 'entities'),
        encoding='utf-8')

    # Entity details
    for name, page in pages.items():
        if page['type'] != 'entities':
            continue
        (ent_dir / f'{name}.html').write_text(generate_detail(page, pages, backlinks), encoding='utf-8')
    print(f"  Generated {len([p for p in pages.values() if p['type'] == 'entities'])} entity pages")

    # Concept listing
    con_dir = OUTPUT_DIR / 'concepts'
    con_dir.mkdir(exist_ok=True)
    (con_dir / 'index.html').write_text(generate_concept_listing(pages, categories), encoding='utf-8')

    # Concept details
    for name, page in pages.items():
        if page['type'] != 'concepts':
            continue
        (con_dir / f'{name}.html').write_text(generate_detail(page, pages, backlinks), encoding='utf-8')
    print(f"  Generated {len([p for p in pages.values() if p['type'] == 'concepts'])} concept pages")

    # Query listing
    q_dir = OUTPUT_DIR / 'queries'
    q_dir.mkdir(exist_ok=True)
    (q_dir / 'index.html').write_text(
        generate_listing(pages, 'queries', '问答', TYPE_DESCRIPTIONS['queries'], 'queries'),
        encoding='utf-8')

    # Query details
    for name, page in pages.items():
        if page['type'] != 'queries':
            continue
        (q_dir / f'{name}.html').write_text(generate_detail(page, pages, backlinks), encoding='utf-8')
    print(f"  Generated {len([p for p in pages.values() if p['type'] == 'queries'])} query pages")

    # Papers listing
    papers_dir = WIKI_ROOT / 'raw' / 'papers'
    if papers_dir.exists():
        p_dir = OUTPUT_DIR / 'papers'
        p_dir.mkdir(exist_ok=True)
        (p_dir / 'index.html').write_text(generate_papers_listing(papers), encoding='utf-8')
        for paper in papers:
            (p_dir / f'{paper["name"]}.html').write_text(generate_paper_detail(paper, pages), encoding='utf-8')
        print(f"  Generated papers listing and {len(papers)} paper pages")

    total = len(list(OUTPUT_DIR.rglob('*.html')))
    print(f"\nDone! Generated {total} HTML pages in {OUTPUT_DIR}")


def detect_changes():
    """Detect what changed between source MD files and existing HTML output."""
    new_pages = []
    modified_pages = []
    deleted_html = []

    for page_type in ['entities', 'concepts', 'queries']:
        type_dir = WIKI_ROOT / page_type
        html_dir = OUTPUT_DIR / page_type
        if not type_dir.exists():
            continue

        for md_file in type_dir.glob('*.md'):
            html_file = html_dir / f'{md_file.stem}.html'
            if not html_file.exists():
                new_pages.append((page_type, md_file.stem, md_file))
            elif md_file.stat().st_mtime > html_file.stat().st_mtime:
                modified_pages.append((page_type, md_file.stem, md_file))

        if html_dir.exists():
            for html_file in html_dir.glob('*.html'):
                if html_file.name == 'index.html':
                    continue
                name = html_file.stem
                md_file = type_dir / f'{name}.md'
                if not md_file.exists():
                    deleted_html.append((page_type, name, html_file))

    papers_dir = WIKI_ROOT / 'raw' / 'papers'
    papers_html_dir = OUTPUT_DIR / 'papers'
    if papers_dir.exists():
        paper_stems = set()
        for md_file in papers_dir.rglob('*.md'):
            paper_stems.add(md_file.stem)
            html_file = papers_html_dir / f'{md_file.stem}.html'
            if not html_file.exists():
                new_pages.append(('papers', md_file.stem, md_file))
            elif md_file.stat().st_mtime > html_file.stat().st_mtime:
                modified_pages.append(('papers', md_file.stem, md_file))

        if papers_html_dir.exists():
            for html_file in papers_html_dir.glob('*.html'):
                if html_file.name == 'index.html':
                    continue
                if html_file.stem not in paper_stems:
                    deleted_html.append(('papers', html_file.stem, html_file))

    # Check structural changes
    structural = []
    for f in [WIKI_ROOT / 'index.md', WIKI_ROOT / 'SCHEMA.md']:
        if f.exists():
            html_dir = OUTPUT_DIR / 'static'
            css_file = html_dir / 'wiki.css'
            if css_file.exists() and f.stat().st_mtime > css_file.stat().st_mtime:
                structural.append(f.name)

    return new_pages, modified_pages, deleted_html, structural


def show_status():
    """Print change detection status."""
    if not OUTPUT_DIR.exists():
        print("No output directory found. Run full generation first.")
        return False

    new_pages, modified_pages, deleted_html, structural = detect_changes()

    print(f"Wiki HTML sync status for {OUTPUT_DIR}")
    print(f"{'=' * 50}")

    if new_pages:
        print(f"\n  NEW ({len(new_pages)}):")
        for pt, name, _ in new_pages:
            print(f"    + {pt}/{name}")
    if modified_pages:
        print(f"\n  MODIFIED ({len(modified_pages)}):")
        for pt, name, _ in modified_pages:
            print(f"    ~ {pt}/{name}")
    if deleted_html:
        print(f"\n  DELETED ({len(deleted_html)}):")
        for pt, name, _ in deleted_html:
            print(f"    - {pt}/{name}")
    if structural:
        print(f"\n  STRUCTURAL CHANGES: {', '.join(structural)}")
        print("  → Full rebuild recommended")

    total = len(new_pages) + len(modified_pages) + len(deleted_html)
    if total == 0 and not structural:
        print("\n  Everything is up to date.")

    return total > 0 or len(structural) > 0


def generate_incremental():
    """Regenerate only changed pages."""
    new_pages, modified_pages, deleted_html, structural = detect_changes()

    needs_full = len(structural) > 0
    if any(pt == 'papers' for pt, _, _ in new_pages + modified_pages + deleted_html):
        needs_full = True
    if needs_full:
        print("Structural or paper changes detected, running full rebuild...")
        generate_all()
        return

    all_changed = new_pages + modified_pages
    if not all_changed and not deleted_html:
        print("Everything is up to date. No changes needed.")
        return

    # Ensure output directories and symlinks exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_dir = OUTPUT_DIR / 'source'
    source_dir.mkdir(exist_ok=True)
    for target in ['entities', 'concepts', 'queries', 'raw', 'papers', 'paper-briefs', 'references']:
        link = source_dir / target
        if (WIKI_ROOT / target).exists() and not link.exists():
            link.symlink_to(WIKI_ROOT / target)

    static_dir = OUTPUT_DIR / 'static'
    if not static_dir.exists():
        static_dir.mkdir(exist_ok=True)
        (static_dir / 'wiki.css').write_text(CSS, encoding='utf-8')
        (static_dir / 'wiki.js').write_text(JS, encoding='utf-8')

    # Load all pages (needed for wikilink resolution and backlinks)
    pages = load_all_pages()
    papers = load_all_papers()
    backlinks = build_backlinks(pages)
    categories = build_concept_categories(pages)

    # Delete removed pages
    for pt, name, html_file in deleted_html:
        html_file.unlink(missing_ok=True)
        print(f"  - Deleted {pt}/{name}.html")

    # Regenerate changed/new pages
    changed_types = set()
    for pt, name, md_file in all_changed:
        page = load_page(md_file, pt)
        if page:
            pages[name] = page
            changed_types.add(pt)

    # Rebuild backlinks for all pages (cheap, done in memory)
    backlinks = build_backlinks(pages)

    # Regenerate affected detail pages
    for pt, name, md_file in all_changed:
        page = pages.get(name)
        if not page:
            continue
        html_dir = OUTPUT_DIR / pt
        html_dir.mkdir(exist_ok=True)
        (html_dir / f'{name}.html').write_text(
            generate_detail(page, pages, backlinks), encoding='utf-8')
        print(f"  {'+' if (pt, name, md_file) in new_pages else '~'} {pt}/{name}.html")

    # Regenerate affected listing pages
    if changed_types:
        categories = build_concept_categories(pages)
        if 'entities' in changed_types:
            ent_dir = OUTPUT_DIR / 'entities'
            ent_dir.mkdir(exist_ok=True)
            (ent_dir / 'index.html').write_text(
                generate_listing(pages, 'entities', '实体', TYPE_DESCRIPTIONS['entities'], 'entities'),
                encoding='utf-8')
            print("  ~ entities/index.html")
        if 'concepts' in changed_types:
            con_dir = OUTPUT_DIR / 'concepts'
            con_dir.mkdir(exist_ok=True)
            (con_dir / 'index.html').write_text(
                generate_concept_listing(pages, categories), encoding='utf-8')
            print("  ~ concepts/index.html")
        if 'queries' in changed_types:
            q_dir = OUTPUT_DIR / 'queries'
            q_dir.mkdir(exist_ok=True)
            (q_dir / 'index.html').write_text(
                generate_listing(pages, 'queries', '问答', TYPE_DESCRIPTIONS['queries'], 'queries'),
                encoding='utf-8')
            print("  ~ queries/index.html")

    # Always update search index and home (they aggregate everything)
    (OUTPUT_DIR / 'search-index.json').write_text(
        generate_search_index(pages, papers), encoding='utf-8')
    (OUTPUT_DIR / 'index.html').write_text(
        generate_home(pages, backlinks, categories), encoding='utf-8')
    (OUTPUT_DIR / 'tags.html').write_text(
        generate_tags_page(pages), encoding='utf-8')

    total = len(new_pages) + len(modified_pages)
    print(f"\nDone! Updated {total} pages ({len(new_pages)} new, {len(modified_pages)} modified, {len(deleted_html)} deleted)")


def serve():
    import http.server
    import socketserver

    os.chdir(OUTPUT_DIR)
    port = 8080
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving at {url}")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate LLM Wiki static site')
    parser.add_argument('--serve', action='store_true', help='Serve the site after generating')
    parser.add_argument('--status', action='store_true', help='Show what changed since last generation')
    parser.add_argument('--incremental', action='store_true', help='Only regenerate changed pages')
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.incremental:
        generate_incremental()
    else:
        generate_all()

    if args.serve:
        serve()
