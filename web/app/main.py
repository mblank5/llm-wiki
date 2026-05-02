"""Wiki Web — Karpathy LLM Wiki Web Interface

Multi-wiki topic management with ArXiv paper ingestion, LLM query, and answer saving.
"""

import os
import re
import json
import glob
import asyncio
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from httpx import AsyncClient

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Wiki Web")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ── LLM Config ──────────────────────────────────────────────
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.longcat.chat/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "LongCat-Flash-Chat-2602-Exp")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ak_2CL8y69Cu9An2GM6j34s49aF5Nc2T")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

WIKIS_ROOT = DATA_DIR / "wikis"
WIKIS_ROOT.mkdir(exist_ok=True)

# ── Helpers ─────────────────────────────────────────────────

def wikirc_config(base_url: str = LLM_BASE_URL, model: str = LLM_MODEL, api_key: str = LLM_API_KEY):
    return {
        "llm": {
            "provider": "openai",
            "model": model,
            "apiKey": api_key,
            "baseUrl": base_url,
            "temperature": LLM_TEMPERATURE,
            "thinking": {"type": "disabled"}
        },
        "wiki": {
            "paths": {
                "raw": "raw",
                "wiki": "wiki",
                "config": ".wikirc.yaml"
            }
        }
    }

def write_wikirc(wiki_dir: Path, base_url=LLM_BASE_URL, model=LLM_MODEL, api_key=LLM_API_KEY):
    config = wikirc_config(base_url, model, api_key)
    import yaml
    wikirc = wiki_dir / ".wikirc.yaml"
    with open(wikirc, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    return wikirc

def wiki_exists(name: str) -> bool:
    return (WIKIS_ROOT / name).is_dir() and (WIKIS_ROOT / name / "wiki").is_dir()

def init_wiki(name: str) -> Path:
    wiki_dir = WIKIS_ROOT / name
    wiki_dir.mkdir(parents=True, exist_ok=True)
    (wiki_dir / "raw" / "untracked").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "raw" / "ingested").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "wiki" / "concepts").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "wiki" / "sources").mkdir(parents=True, exist_ok=True)
    (wiki_dir / "wiki" / "log.md").write_text("# Operations Log\n")
    # Write wiki index
    idx = wiki_dir / "wiki" / "index.md"
    idx.write_text("# Wiki Index\n\nAuto-generated.\n\n## Sources\n*No sources yet.*\n\n## Concepts\n*No concepts yet.*\n")
    # Write .wikirc.yaml using yaml if available, else manual
    import yaml
    config = wikirc_config()
    with open(wiki_dir / ".wikirc.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    return wiki_dir

def list_wikis():
    wikis = []
    for d in sorted(WIKIS_ROOT.iterdir()):
        if d.is_dir() and (d / "wiki").is_dir():
            ingested = len(list(d.glob("raw/ingested/**/*.md")))
            concepts = len(list(d.glob("wiki/concepts/*.md")))
            sources = len(list(d.glob("wiki/sources/*.md")))
            # Read description from first line of log
            log = d / "wiki" / "log.md"
            desc = ""
            if log.exists():
                lines = log.read_text().strip().split("\n")
                for l in lines[1:3]:
                    if l.startswith("## ["):
                        desc = l.replace("## [", "").strip()
                        break
            wikis.append({
                "name": d.name,
                "path": str(d),
                "papers": ingested,
                "concepts": concepts,
                "sources": sources,
                "description": desc,
                "created": datetime.fromtimestamp(d.stat().st_mtime).strftime("%Y-%m-%d") if d.stat().st_mtime else "unknown"
            })
    return wikis

def extract_arxiv_month_year(arxiv_id: str):
    """Extract year/month from arxiv ID like 2501.11120 or 1511.06295"""
    match = re.match(r'(\d{2})(\d{2})', arxiv_id.replace('v', '').split('.')[0])
    if not match:
        return "2026", "01"
    y, m = match.group(1), match.group(2)
    year = f"20{y}"
    return year, m

async def llm_chat(messages: list, model: str = LLM_MODEL, temperature: float = LLM_TEMPERATURE):
    """Call LLM API"""
    async with AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

async def arxiv2md(arxiv_id: str, output_path: str) -> dict:
    """Run arxiv2md and return metadata"""
    try:
        result = subprocess.run(
            ["arxiv2md", arxiv_id, "-o", output_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # Parse summary from stderr/stdout
            summary = {}
            output = result.stdout + result.stderr
            for line in output.split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    summary[key.strip().lower()] = val.strip()
            return {"status": "ok", "output": output_path, "summary": summary}
        else:
            return {"status": "error", "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout converting paper"}
    except FileNotFoundError:
        return {"status": "error", "error": "arxiv2md not found"}

async def wiki_ingest(wiki_dir: Path, rel_path: str) -> dict:
    """Run wiki ingest for a single paper"""
    try:
        wikirc = wiki_dir / ".wikirc.yaml"
        if not wikirc.exists():
            write_wikirc(wiki_dir)

        result = subprocess.run(
            ["wiki", "ingest", rel_path, "-y"],
            capture_output=True, text=True, timeout=300,
            cwd=str(wiki_dir)
        )
        if result.returncode == 0:
            # Parse operations
            ops = []
            if "Proposed Operations" in result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip().startswith("["):
                        ops.append(line.strip())
            return {"status": "ok", "stdout": result.stdout, "operations": ops}
        else:
            return {"status": "error", "error": result.stderr[:500] if result.stderr else result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "Ingest timed out after 5 minutes"}

async def wiki_query_full(wiki_dir: Path, question: str, max_iterations: int = 4):
    """Run wiki query with ReAct-style iteration.
    Returns streaming text answer.
    """
    wikirc = wiki_dir / ".wikirc.yaml"
    if not wikirc.exists():
        write_wikirc(wiki_dir)

    wiki_path = wiki_dir / "wiki"
    raw_path = wiki_dir / "raw" / "ingested"

    # Read index
    index_md = wiki_path / "index.md"
    index_content = index_md.read_text() if index_md.exists() else "# Wiki Index\nEmpty"

    # List available concept/source pages for context
    concept_files = sorted(wiki_path.glob("concepts/*.md"))
    source_files = sorted(wiki_path.glob("sources/*.md"))
    ingested_files = sorted(raw_path.glob("**/*.md"))

    # Build prompt
    system_prompt = f"""You are a research assistant answering questions based on a personal knowledge base wiki.

The wiki contains papers organized by topic. You have access to the following resources:

Wiki Index:
{index_content[:3000]}

Concept Pages: {', '.join(f.stem for f in concept_files[:20])}
Source Pages: {', '.join(f.stem for f in source_files[:20])}

Rules:
1. Answer based ONLY on the content provided below. If you don't know, say so.
2. Cite sources with [src: ARXIV_ID] notation.
3. Use markdown formatting for structure (headings, tables, lists).
4. Be thorough and detailed in your answers.
5. Respond in the same language as the question (Chinese if asked in Chinese, English if asked in English).
"""

    # Read all relevant content
    all_content = []

    # Read concept pages
    for cf in concept_files[:15]:
        try:
            content = cf.read_text()
            all_content.append(f"## Concept: {cf.stem}\n{content[:2000]}")
        except:
            pass

    # Read source pages
    for sf in source_files[:15]:
        try:
            content = sf.read_text()
            all_content.append(f"## Source: {sf.stem}\n{content[:1500]}")
        except:
            pass

    # Read key sections of ingested papers (first 500 chars each for context)
    for pf in ingested_files[:10]:
        try:
            content = pf.read_text()
            # Get title and abstract
            abstract_match = re.search(r'## Abstract(.*?)(?=## \d|$)', content, re.DOTALL)
            if abstract_match:
                all_content.append(f"## Paper Abstract: {pf.stem}\n## Abstract{abstract_match.group(1)[:1000]}")
            # Get first 500 chars
            all_content.append(f"## Paper Header: {pf.stem}\n{content[:500]}")
        except:
            pass

    context = "\n\n---\n\n".join(all_content[:25])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {question}\n\nHere is the wiki content:\n\n{context[:15000]}"}
    ]

    answer = await llm_chat(messages)
    return answer

async def wiki_query_stream(wiki_dir: Path, question: str):
    """Stream wiki query response using OpenAI streaming API."""
    wiki_path = wiki_dir / "wiki"
    raw_path = wiki_dir / "raw" / "ingested"

    index_md = wiki_path / "index.md"
    index_content = index_md.read_text() if index_md.exists() else "# Wiki Index\nEmpty"

    concept_files = sorted(wiki_path.glob("concepts/*.md"))
    source_files = sorted(wiki_path.glob("sources/*.md"))
    ingested_files = sorted(raw_path.glob("**/*.md"))

    system_prompt = f"""You are a research assistant answering questions based on a personal knowledge base wiki.

Wiki Index:
{index_content[:3000]}

Concept Pages: {', '.join(f.stem for f in concept_files[:20])}
Source Pages: {', '.join(f.stem for f in source_files[:20])}

Rules:
1. Answer based ONLY on the wiki content provided. If you don't know, say so.
2. Cite sources with [src: ARXIV_ID] notation.
3. Use markdown formatting.
4. Be thorough and detailed.
5. Respond in the same language as the question.
"""

    all_content = []
    for cf in concept_files[:15]:
        try:
            content = cf.read_text()
            all_content.append(f"## Concept: {cf.stem}\n{content[:2000]}")
        except:
            pass
    for sf in source_files[:15]:
        try:
            all_content.append(f"## Source: {sf.stem}\n{sf.read_text()[:1500]}")
        except:
            pass
    for pf in ingested_files[:10]:
        try:
            content = pf.read_text()
            abstract_match = re.search(r'## Abstract(.*?)(?=## \d|$)', content, re.DOTALL)
            if abstract_match:
                all_content.append(f"## Paper: {pf.stem}\n## Abstract{abstract_match.group(1)[:1000]}")
            else:
                all_content.append(f"## Paper: {pf.stem}\n{content[:500]}")
        except:
            pass

    context = "\n\n---\n\n".join(all_content[:25])

    async with AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question}\n\nWiki content:\n\n{context[:15000]}"}
                ],
                "temperature": LLM_TEMPERATURE,
                "stream": True
            }
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue

# ── Models ──────────────────────────────────────────────────

class WikiCreateReq(BaseModel):
    name: str

class AddPaperReq(BaseModel):
    arxiv_id: str

class QueryReq(BaseModel):
    question: str
    save_as: Optional[str] = None

# ── Routes: API ─────────────────────────────────────────────

@app.get("/api/wikis")
def api_list_wikis():
    return {"wikis": list_wikis()}

@app.post("/api/wikis")
def api_create_wiki(req: WikiCreateReq):
    # Validate name
    if not re.match(r'^[a-z0-9][a-z0-9_-]{0,40}$', req.name):
        raise HTTPException(400, "Name must be lowercase letters, numbers, hyphens, underscores (max 41 chars)")
    if wiki_exists(req.name):
        raise HTTPException(400, f"Wiki '{req.name}' already exists")

    wiki_dir = init_wiki(req.name)
    return {"status": "ok", "name": req.name, "path": str(wiki_dir)}

@app.get("/api/wikis/{name}/papers")
def api_list_papers(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    papers = []
    for f in sorted(wiki_dir.glob("raw/ingested/**/*.md"), reverse=True):
        aid = f.stem
        # Try to extract title from first line
        try:
            first_line = f.read_text().split("\n")[0]
            title = first_line.replace("Title: ", "").strip() if first_line.startswith("Title:") else aid
        except:
            title = aid
        papers.append({"id": aid, "title": title, "path": str(f.relative_to(wiki_dir))})

    return {"papers": papers}

@app.get("/api/wikis/{name}/concepts")
def api_list_concepts(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    concepts = []
    for f in sorted(wiki_dir.glob("wiki/concepts/*.md")):
        try:
            content = f.read_text()
            first_para = ""
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    first_para = stripped[:120]
                    break
            concepts.append({"name": f.stem, "path": str(f.relative_to(wiki_dir / "wiki")), "preview": first_para})
        except:
            concepts.append({"name": f.stem, "path": str(f.relative_to(wiki_dir / "wiki")), "preview": ""})

    return {"concepts": concepts}

@app.post("/api/wikis/{name}/add-paper")
async def api_add_paper(name: str, req: AddPaperReq):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    arxiv_id = req.arxiv_id.strip()
    year, month = extract_arxiv_month_year(arxiv_id)
    untracked_dir = wiki_dir / "raw" / "untracked" / year / month
    untracked_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(untracked_dir / f"{arxiv_id}.md")

    result = await arxiv2md(arxiv_id, output_path)
    return result

@app.post("/api/wikis/{name}/ingest")
async def api_ingest_paper(name: str, paper_id: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    # Find the paper in untracked
    found = None
    for f in wiki_dir.glob("raw/untracked/**/*.md"):
        if f.stem == paper_id:
            found = f
            break

    if not found:
        # Maybe already ingested?
        for f in wiki_dir.glob("raw/ingested/**/*.md"):
            if f.stem == paper_id:
                return {"status": "already_ingested", "path": str(f)}
        raise HTTPException(404, f"Paper {paper_id} not found in untracked")

    rel_path = str(found.relative_to(wiki_dir / "raw" / "untracked"))
    result = await wiki_ingest(wiki_dir, rel_path)
    return result

@app.post("/api/wikis/{name}/add-pending-paper")
async def api_add_pending_paper(name: str):
    """Find first pending paper in untracked and ingest it."""
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    pending = sorted(wiki_dir.glob("raw/untracked/**/*.md"))
    if not pending:
        return {"status": "ok", "message": "No pending papers"}

    found = pending[0]
    rel_path = str(found.relative_to(wiki_dir / "raw" / "untracked"))
    result = await wiki_ingest(wiki_dir, rel_path)
    result["paper_id"] = found.stem
    return result

@app.get("/api/wikis/{name}/pending")
def api_list_pending(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    pending = []
    for f in sorted(wiki_dir.glob("raw/untracked/**/*.md")):
        pending.append({"id": f.stem, "path": str(f.relative_to(wiki_dir))})
    return {"pending": pending}

@app.get("/api/wikis/{name}/content/{content_type}/{filename}")
def api_get_content(name: str, content_type: str, filename: str):
    """Get wiki page content as markdown."""
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    # Sanitize filename
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    file_path = wiki_dir / "wiki" / content_type / f"{safe_name}.md"

    if not file_path.exists():
        raise HTTPException(404, f"Page not found: {content_type}/{safe_name}")

    return {"name": safe_name, "content": file_path.read_text()}

@app.get("/api/wikis/{name}/log")
def api_get_log(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    log_path = wiki_dir / "wiki" / "log.md"
    if not log_path.exists():
        return {"log": ""}

    return {"log": log_path.read_text()}

@app.get("/api/wikis/{name}/index")
def api_get_index(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    idx_path = wiki_dir / "wiki" / "index.md"
    if not idx_path.exists():
        return {"index": ""}

    return {"index": idx_path.read_text()}

@app.post("/api/wikis/{name}/rebuild-index")
def api_rebuild_index(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    ingested = sorted(wiki_dir.glob("raw/ingested/**/*.md"))
    concepts = sorted(wiki_dir.glob("wiki/concepts/*.md"))

    lines = ["# Wiki Index\n\n", f"Auto-generated. Last rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
             f"\n## Sources ({len(ingested)} papers)\n"]
    for p in ingested:
        lines.append(f"- **{p.stem}**\n")

    lines.append(f"\n## Concepts ({len(concepts)} concepts)\n")
    for p in concepts:
        try:
            content = p.read_text()
            first_para = ''
            for l in content.split('\n'):
                s = l.strip()
                if s and not s.startswith('#'):
                    first_para = s[:120]
                    break
            lines.append(f"- [[{p.stem}]]" + (f" — {first_para}" if first_para else '') + "\n")
        except:
            lines.append(f"- [[{p.stem}]]\n")

    idx_path = wiki_dir / "wiki" / "index.md"
    idx_path.write_text(''.join(lines))

    return {"status": "ok", "sources": len(ingested), "concepts": len(concepts)}

# Query - SSE streaming endpoint
@app.post("/api/wikis/{name}/query-stream")
async def api_query_stream(name: str, req: QueryReq):
    from fastapi.responses import StreamingResponse
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    async def event_stream():
        try:
            full_answer = ""
            async for chunk in wiki_query_stream(wiki_dir, req.question):
                full_answer += chunk
                # Use SERVER-SENT EVENTS format
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"

            # Save if requested
            if req.save_as:
                answers_dir = wiki_dir / "wiki" / "answers"
                answers_dir.mkdir(exist_ok=True)
                safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5 _.--]', '', req.save_as)
                answer_file = answers_dir / f"{safe_name}.md"
                answer_file.write_text(f"# {req.question}\n\n{full_answer}\n\n> [generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")

            yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_length': len(full_answer), 'saved': bool(req.save_as)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# Non-streaming query for simpler clients
@app.post("/api/wikis/{name}/query")
async def api_query(name: str, req: QueryReq):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    answer = await wiki_query_full(wiki_dir, req.question)

    if req.save_as:
        answers_dir = wiki_dir / "wiki" / "answers"
        answers_dir.mkdir(exist_ok=True)
        safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5 _.--]', '', req.save_as)
        answer_file = answers_dir / f"{safe_name}.md"
        answer_file.write_text(f"# {req.question}\n\n{answer}\n\n> [generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")
        return {"answer": answer, "saved": True, "saved_as": req.save_as}

    return {"answer": answer}

@app.get("/api/wikis/{name}/answers")
def api_list_answers(name: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    answers = []
    for f in sorted((wiki_dir / "wiki" / "answers").glob("*.md"), reverse=True):
        answers.append({
            "name": f.stem,
            "path": str(f.relative_to(wiki_dir / "wiki")),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        })
    return {"answers": answers}

@app.get("/api/wikis/{name}/answers/{filename}")
def api_get_answer(name: str, filename: str):
    wiki_dir = WIKIS_ROOT / name
    if not wiki_exists(name):
        raise HTTPException(404, "Wiki not found")

    safe = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5 _.--]', '', filename)
    file_path = wiki_dir / "wiki" / "answers" / f"{safe}.md"
    if not file_path.exists():
        raise HTTPException(404, "Answer not found")

    return {"name": safe, "content": file_path.read_text()}

# ── Routes: HTML Pages ──────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def page_home(request: Request):
    wikis = list_wikis()
    return templates.TemplateResponse("home.html", {"request": request, "wikis": wikis})

@app.get("/wiki/{name}", response_class=HTMLResponse)
async def page_wiki(request: Request, name: str):
    if not wiki_exists(name):
        return HTMLResponse("<h1>Wiki not found</h1><a href='/'>Back</a>")
    return templates.TemplateResponse("wiki.html", {"request": request, "wiki_name": name})

@app.get("/wiki/{name}/chat", response_class=HTMLResponse)
async def page_chat(request: Request, name: str):
    if not wiki_exists(name):
        return HTMLResponse("<h1>Wiki not found</h1><a href='/'>Back</a>")
    return templates.TemplateResponse("chat.html", {"request": request, "wiki_name": name})

# ── Static ──────────────────────────────────────────────────

@app.get("/manifest.json")
def manifest():
    return FileResponse(BASE_DIR / "static" / "manifest.json")

@app.get("/sw.js")
def service_worker():
    return FileResponse(BASE_DIR / "static" / "sw.js")
