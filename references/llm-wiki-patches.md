# llm-wiki Code Patches — Detailed Reference

This document describes the 4 patches applied to the upstream `llm-wiki` npm package for reliable operation with ArXiv papers.

## Finding the Install Path

```bash
find "$(npm root -g)/llm-wiki" -name "wiki.js" -path "*/dist/bin/*"
# e.g. /home/mblank/.nvm/versions/node/v24.14.0/lib/node_modules/llm-wiki/dist/bin/wiki.js
```

## Patch 1: chatJSON() Method

**File:** `dist/bin/wiki.js`
**Location:** Inside the `LLMClient` class, after the existing `chat()` method.

**Purpose:** Adds a `chatJSON()` method that sets `response_format: { type: "json_object" }` on OpenAI-compatible API calls, forcing the LLM to output valid JSON for ingest/query operations.

```javascript
async chatJSON(messages) {
  const opts = {
    model: this.config.llm.model,
    messages,
    temperature: this.config.llm.temperature,
    thinking: this.config.llm.thinking,
    response_format: { type: "json_object" }
  };
  const response = await this.client.chat.completions.create(opts);
  return response.choices[0]?.message?.content || null;
}
```

## Patch 2: Use chatJSON in Ingest

**File:** `dist/bin/wiki.js` (same as Patch 1)
**Find:** `const response = await llm.chat([{ role: "user", content: promptText }]);`
**Replace with:** `const response = await llm.chatJSON([{ role: "user", content: promptText }]);`

**Purpose:** The ingest flow needs JSON output. Forcing json_object response format dramatically reduces JSON parse failures.

## Patch 3: No LaTeX in Agent Prompt

**File:** `dist/schemas/agent.md`
**Action:** Append rule #7 to the end of the file.

```
7. **No LaTeX in wiki content**: When writing page content in JSON, NEVER use LaTeX
math notation (`$...$`, `$$...$$`, `\varphi`, `\psi`, etc.). Use plain text
descriptions instead (e.g., write "z in Z" instead of "$z \in Z$"). This prevents
JSON encoding errors with backslashes and dollar signs.
```

**Purpose:** LaTeX formulas in LLM output JSON cause double-escaping issues that break `jsonrepair`. Plain text avoids the problem entirely.

## Patch 4: Fix Recursive Path Lookup

**File:** `dist/bin/wiki.js` (inside the `WikiManager` class, after `getWikiRoot()`)

**Purpose:** The `getPageContents()` method tries to find papers by exact path like `raw/ingested/2505.09388.md`, but papers are actually stored in subdirectories `raw/ingested/2025/05/2505.09388.md`. When the direct path fails, the fallback `scanDir()` skips it because `t.isPath = true`. This adds a `_findFileRecursive()` helper that searches recursively.

```javascript
async _findFileRecursive(dir, targetBasename) {
  if (!await fs5.pathExists(dir)) return null;
  const entries = await fs5.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path5.join(dir, entry.name);
    if (entry.isDirectory()) {
      const found = await this._findFileRecursive(fullPath, targetBasename);
      if (found) return found;
    } else if (entry.isFile() && entry.name === targetBasename) {
      return fullPath;
    }
  }
  return null;
}
```

Then in `getPageContents()`, after the direct path lookup fails:
```javascript
if (!found) {
  const basename = t.original.split("/").pop();
  const ingestedDir = path5.join(this.config.wikiRoot, this.config.paths.raw, "ingested");
  try {
    const foundFile = await this._findFileRecursive(ingestedDir, basename);
    if (foundFile) {
      const content = await fs5.readFile(foundFile, "utf8");
      results.push({ name: t.original, content });
      targets.splice(i, 1);
    }
  } catch {}
}
```

## Verify Patches Applied

```bash
LLM_WIKI=$(find "$(npm root -g)/llm-wiki" -name "wiki.js" | head -1 | xargs dirname)

grep "chatJSON" "$LLM_WIKI/dist/bin/wiki.js"
grep "No LaTeX" "$LLM_WIKI/dist/schemas/agent.md"
grep "_findFileRecursive" "$LLM_WIKI/dist/bin/wiki.js"
```

All four should return results.
