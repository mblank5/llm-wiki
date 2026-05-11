#!/usr/bin/env python3
"""Build Chinese paper brief cards from raw/cleaned paper Markdown.

The rendered website treats raw papers as evidence, not as final reading
material. This script creates durable Chinese notes under paper-briefs/ so the
paper HTML pages can present a research card first and link to source material
second.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from openai import OpenAI


WIKI_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = WIKI_ROOT / "raw" / "papers"
CLEAN_DIR = WIKI_ROOT / "papers"
BRIEF_DIR = WIKI_ROOT / "paper-briefs"

MAX_INPUT_CHARS = 52000
MIN_USEFUL_SOURCE_CHARS = 1200


SYSTEM_PROMPT = """你是中文 AI/ML 研究知识库编辑。你的任务不是逐字翻译论文，而是把论文整理成可读、可检索、可复用的中文研究卡片。

要求：
1. 输出必须是合法 JSON 对象，不要 Markdown 代码块，不要额外解释。
2. 使用中文，保留必要英文术语和关键数字。
3. 不要编造论文没有提供的结论；如果源材料不足，明确说明。
4. 内容要面向研究者：讲清楚问题、方法、实验、局限、适合沉淀到 wiki 的概念。
5. 每个要点必须具体，不要写“效果很好”“具有重要意义”这类空话。

JSON 字段：
- title_zh: 中文标题，不超过 40 字
- paper_type: 论文类型，如 benchmark / method / model / system / survey / dataset / analysis
- one_liner: 一句话定位，说明这篇论文解决什么问题、核心做法是什么
- why_it_matters: 3-5 条，为什么值得记录
- method: 4-7 条，核心方法/系统设计/训练流程
- results: 3-6 条，关键实验结果或定量发现；没有数字就说明没有可靠数字
- limitations: 2-5 条，局限、风险或复现注意点
- concept_links: 4-8 个适合转成 wiki 概念的短语，使用小写连字符英文或中英混合短语
- reading_notes: 3-5 条，阅读时应该关注的细节
- quality: ok / source_limited
- quality_note: 对源材料完整性的判断
"""


def load_config(root: Path) -> dict[str, str]:
    env_path = root / ".env"
    cfg = dotenv_values(env_path) if env_path.exists() else {}
    return {
        "api_base": os.environ.get("PAPER_API_BASE", cfg.get("PAPER_API_BASE", "")),
        "api_key": os.environ.get("PAPER_API_KEY", cfg.get("PAPER_API_KEY", "")),
        "model": os.environ.get("PAPER_MODEL", cfg.get("PAPER_MODEL", "gpt-4o")),
    }


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, parts[2].strip()


def clean_inline(text: str) -> str:
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_title(text: str, fallback: str) -> str:
    meta, body = split_frontmatter(text)
    if meta.get("title"):
        return str(meta["title"])
    for line in body.splitlines()[:80]:
        stripped = clean_inline(line.strip())
        if line.startswith("# ") and len(stripped) > 4:
            return stripped.lstrip("# ").strip()
        if stripped.lower().startswith("title:"):
            return stripped.split(":", 1)[1].strip()
    return fallback


def paper_paths(root: Path) -> list[Path]:
    return sorted((root / "raw" / "papers").rglob("*.md"), reverse=True)


def existing_brief_quality(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")[:800]
    match = re.search(r'^quality:\s*["\']?([^"\'\n]+)', text, re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


def best_source(raw_path: Path, root: Path) -> tuple[Path, str]:
    rel = raw_path.relative_to(root / "raw" / "papers")
    clean_path = root / "papers" / rel
    if clean_path.exists() and clean_path.stat().st_size > raw_path.stat().st_size:
        return clean_path, "clean"
    return raw_path, "raw"


def read_for_model(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) <= MAX_INPUT_CHARS:
        return text
    head = text[: MAX_INPUT_CHARS * 2 // 3]
    tail = text[-MAX_INPUT_CHARS // 3 :]
    return f"{head}\n\n[...中间内容因长度截断...]\n\n{tail}"


def listify(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def yaml_scalar(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def fallback_brief(
    raw_path: Path,
    source_path: Path,
    source_kind: str,
    title: str,
    reason: str,
    quality: str = "source_limited",
    heading: str | None = None,
) -> str:
    rel = raw_path.relative_to(RAW_DIR).as_posix()
    arxiv_id = raw_path.stem
    today = time.strftime("%Y-%m-%d")
    heading = heading or f"源材料不足：{arxiv_id}"
    return f"""---
title: {yaml_scalar(title)}
title_zh: {yaml_scalar(heading)}
arxiv_id: {yaml_scalar(arxiv_id)}
source_kind: {yaml_scalar(source_kind)}
raw_path: {yaml_scalar(f"raw/papers/{rel}")}
generated: {yaml_scalar(today)}
quality: {yaml_scalar(quality)}
---

# {heading}

## 一句话定位

当前页面是中文占位卡片，暂时无法生成可靠的完整精读摘要。

## 质量说明

- 源文件：`raw/papers/{rel}`
- 采用来源：`{source_kind}`，`{source_path.relative_to(WIKI_ROOT).as_posix()}`
- 问题：{reason}
- 处理建议：补充源材料或恢复模型额度后，重新运行 `scripts/build-paper-briefs.py` 生成正式中文卡片。

## 原文入口

保留源 Markdown / 清洗稿作为证据入口，避免用不完整材料生成误导性摘要。
"""


def render_markdown(raw_path: Path, source_path: Path, source_kind: str, data: dict[str, Any], title: str, model: str) -> str:
    rel = raw_path.relative_to(RAW_DIR).as_posix()
    arxiv_id = raw_path.stem
    today = time.strftime("%Y-%m-%d")
    title_zh = str(data.get("title_zh") or title).strip()
    paper_type = str(data.get("paper_type") or "paper").strip()
    quality = str(data.get("quality") or "ok").strip()
    quality_note = str(data.get("quality_note") or "").strip()

    def bullets(key: str) -> str:
        values = listify(data.get(key))
        if not values:
            return "- 暂无可靠信息。"
        return "\n".join(f"- {value}" for value in values)

    concepts = listify(data.get("concept_links"))
    concept_line = ", ".join(f"`{c}`" for c in concepts) if concepts else "暂无"

    return f"""---
title: {yaml_scalar(title)}
title_zh: {yaml_scalar(title_zh)}
arxiv_id: {yaml_scalar(arxiv_id)}
paper_type: {yaml_scalar(paper_type)}
source_kind: {yaml_scalar(source_kind)}
raw_path: {yaml_scalar(f"raw/papers/{rel}")}
generated: {yaml_scalar(today)}
model: {yaml_scalar(model)}
quality: {yaml_scalar(quality)}
---

# {title_zh}

## 一句话定位

{str(data.get("one_liner") or "暂无可靠定位。").strip()}

## 为什么值得记录

{bullets("why_it_matters")}

## 核心方法

{bullets("method")}

## 关键结果

{bullets("results")}

## 局限与风险

{bullets("limitations")}

## 适合沉淀的概念

{concept_line}

## 阅读注意

{bullets("reading_notes")}

## 质量说明

- 采用来源：`{source_kind}`，`{source_path.relative_to(WIKI_ROOT).as_posix()}`
- 生成模型：`{model}`
- 源材料判断：{quality_note or quality}
"""


def parse_json_object(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
        raise


def call_model_once(client: OpenAI, model: str, paper_id: str, title: str, source_kind: str, text: str) -> dict[str, Any]:
    user_msg = f"""Paper ID: {paper_id}
Title: {title}
Source kind: {source_kind}

论文材料：

{text}
"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=2600,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    return parse_json_object(content)


def call_model(client: OpenAI, model: str, paper_id: str, title: str, source_kind: str, text: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            return call_model_once(client, model, paper_id, title, source_kind, text)
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{paper_id}: model did not return valid JSON after retries: {last_error}")


def process_one(raw_path: Path, root: Path, cfg: dict[str, str], force: bool) -> tuple[str, str]:
    rel = raw_path.relative_to(root / "raw" / "papers")
    out_path = root / "paper-briefs" / rel
    if out_path.exists() and not force and existing_brief_quality(out_path) != "pending_brief":
        return raw_path.stem, "skip"

    source_path, source_kind = best_source(raw_path, root)
    source_text = source_path.read_text(encoding="utf-8", errors="ignore")
    title = extract_title(source_text, raw_path.stem)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if len(source_text.strip()) < MIN_USEFUL_SOURCE_CHARS:
        out_path.write_text(
            fallback_brief(raw_path, source_path, source_kind, title, "源文本过短，无法支撑可靠总结。"),
            encoding="utf-8",
        )
        return raw_path.stem, "source_limited"

    client = OpenAI(base_url=cfg["api_base"], api_key=cfg["api_key"])
    model_input = read_for_model(source_path)
    data = call_model(client, cfg["model"], raw_path.stem, title, source_kind, model_input)
    out_path.write_text(render_markdown(raw_path, source_path, source_kind, data, title, cfg["model"]), encoding="utf-8")
    return raw_path.stem, "ok"


def write_pending_brief(raw_path: Path, root: Path, reason: str) -> tuple[str, str]:
    rel = raw_path.relative_to(root / "raw" / "papers")
    out_path = root / "paper-briefs" / rel
    if out_path.exists():
        return raw_path.stem, "skip"
    source_path, source_kind = best_source(raw_path, root)
    source_text = source_path.read_text(encoding="utf-8", errors="ignore")
    title = extract_title(source_text, raw_path.stem)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        fallback_brief(
            raw_path,
            source_path,
            source_kind,
            title,
            reason,
            quality="pending_brief",
            heading=f"待中文精读：{raw_path.stem}",
        ),
        encoding="utf-8",
    )
    return raw_path.stem, "pending_brief"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Chinese paper brief cards")
    parser.add_argument("wiki_root", nargs="?", default=".", help="Repository/wiki root")
    parser.add_argument("--limit", type=int, help="Maximum papers to process")
    parser.add_argument("--force", action="store_true", help="Regenerate existing briefs")
    parser.add_argument("--ids", nargs="+", help="Only process these paper IDs")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent API workers")
    parser.add_argument("--dry-run", action="store_true", help="Show planned work")
    parser.add_argument(
        "--fallback-missing",
        action="store_true",
        help="Create Chinese pending cards for missing briefs without calling the API",
    )
    args = parser.parse_args()

    root = Path(args.wiki_root).resolve()
    cfg = load_config(root)
    if not cfg["api_key"] and not args.dry_run and not args.fallback_missing:
        print("Error: Set PAPER_API_KEY in .env or environment", file=sys.stderr)
        return 1

    raw_paths = paper_paths(root)
    if args.ids:
        wanted = set(args.ids)
        raw_paths = [p for p in raw_paths if p.stem in wanted]
    if not args.force:
        filtered = []
        for path in raw_paths:
            brief_path = root / "paper-briefs" / path.relative_to(root / "raw" / "papers")
            quality = existing_brief_quality(brief_path)
            if not quality or quality == "pending_brief":
                filtered.append(path)
        raw_paths = filtered
    if args.limit:
        raw_paths = raw_paths[: args.limit]

    print(f"Model: {cfg['model']}")
    print(f"To process: {len(raw_paths)}")
    if args.dry_run:
        for p in raw_paths:
            source, kind = best_source(p, root)
            print(f"  {p.stem}: {kind} {source.relative_to(root)}")
        return 0
    if not raw_paths:
        return 0

    if args.fallback_missing:
        pending = 0
        skipped_pending = 0
        reason = "模型额度或网络条件暂时不足，尚未生成正式中文精读卡片。"
        for path in raw_paths:
            _, status = write_pending_brief(path, root, reason)
            if status == "pending_brief":
                pending += 1
            else:
                skipped_pending += 1
            print(f"{path.stem}: {status}", flush=True)
        print(f"Done. pending_brief={pending}, skipped={skipped_pending}")
        return 0

    ok = 0
    skipped = 0
    limited = 0
    errors = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(process_one, p, root, cfg, args.force): p for p in raw_paths}
        for future in as_completed(futures):
            try:
                paper_id, status = future.result()
                if status == "ok":
                    ok += 1
                elif status == "source_limited":
                    limited += 1
                else:
                    skipped += 1
                print(f"{paper_id}: {status}", flush=True)
            except Exception as exc:
                errors += 1
                paper = futures[future]
                print(f"{paper.stem}: ERROR: {exc}", flush=True)

    print(f"Done. ok={ok}, source_limited={limited}, skipped={skipped}, errors={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
