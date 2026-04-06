#!/bin/bash
# setup-arxiv-wiki.sh — One-shot setup for Karpathy LLM Wiki
# Usage: bash setup-arxiv-wiki.sh [wiki_dir] [base_url] [model] [api_key]
# Example:
#   bash setup-arxiv-wiki.sh ~/my-wiki https://api.longcat.chat/openai/v1 LongCat-Flash-Chat ak_xxx
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIKI_DIR="${1:-.}"
BASE_URL="${2:-}"
MODEL="${3:-}"
API_KEY="${4:-}"

echo "=== Karpathy LLM Wiki Setup ==="
echo ""

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "ERROR: node is required"; exit 1; }
command -v arxiv2md >/dev/null 2>&1 || { echo "ERROR: arxiv2md is required"; exit 1; }

# Install llm-wiki
echo "[1/4] Installing llm-wiki..."
npm install -g llm-wiki 2>/dev/null || echo "  (llm-wiki may already be installed)"

# Find llm-wiki location
LLM_WIKI_ROOT="$(npm root -g)/llm-wiki"
WIKI_JS=$(find "$LLM_WIKI_ROOT" -name "wiki.js" -path "*/dist/bin/*" | head -1)
AGENT_MD=$(find "$LLM_WIKI_ROOT" -name "agent.md" -path "*/schemas/*" | head -1)

echo "[2/4] Applying patches..."

if [ -n "$WIKI_JS" ]; then
    for patch_file in "$SCRIPT_DIR/patches/"*.patch; do
        [ -f "$patch_file" ] || continue
        filename=$(basename "$patch_file")

        case "$filename" in
            *chatjson.patch|*use-chatjson.patch)
                if [ -n "$WIKI_JS" ]; then
                    patch_path="$WIKI_JS"
                fi
                ;;
            *no-latex.patch|*agent.patch)
                patch_path="$AGENT_MD"
                ;;
            *path-lookup.patch)
                patch_path="$WIKI_JS"
                ;;
            *)
                echo "  SKIP: $filename (unknown target)"
                continue
                ;;
        esac

        if [ -z "$patch_path" ] || [ ! -f "$patch_path" ]; then
            echo "  SKIP: $filename (target not found: $patch_path)"
            continue
        fi

        # Try fuzzy-patch approach (the patch files are descriptive, not strict git format)
        # Instead of 'patch -p1', we use a targeted sed approach
        case "$filename" in
            *01-chatjson.patch)
                if grep -q "async chatJSON" "$patch_path" 2>/dev/null; then
                    echo "  SKIP: chatJSON() already exists"
                else
                    # Insert chatJSON method after the chat() method closing
                    sed -i '/return response\.choices\[0\]?.message?.content || null;/{
a\  }\
  async chatJSON(messages) {\
    const opts = {\
      model: this.config.llm.model,\
      messages,\
      temperature: this.config.llm.temperature,\
      thinking: this.config.llm.thinking,\
      response_format: { type: "json_object" }\
    };\
    const response = await this.client.chat.completions.create(opts);\
    return response.choices[0]?.message?.content || null;
                    }' "$patch_path" 2>/dev/null || {
                        echo "  WARN: patch 01 failed via sed, see references/llm-wiki-patches.md for manual fix"
                        continue
                    }
                    echo "  OK: 01-chatjson"
                fi
                ;;
            *02-use-chatjson.patch)
                if grep -q "chatJSON" "$patch_path" 2>/dev/null; then
                    echo "  SKIP: chatJSON already used in ingest"
                else
                    sed -i 's/await llm\.chat(\[{ role: "user", content: promptText }\]);/await llm.chatJSON([{ role: "user", content: promptText }]);/' "$patch_path"
                    echo "  OK: 02-use-chatjson-ingest"
                fi
                ;;
            *03-no-latex.patch)
                if grep -q "No LaTeX" "$patch_path" 2>/dev/null; then
                    echo "  SKIP: No LaTeX rule already exists"
                else
                    echo '' >> "$patch_path"
                    echo '7. **No LaTeX in wiki content**: When writing page content in JSON, NEVER use LaTeX math notation (`$...$`, `$$...$$`, `\varphi`, `\psi`, etc.). Use plain text descriptions instead.' >> "$patch_path"
                    echo "  OK: 03-no-latex-agent"
                fi
                ;;
            *04-path-lookup.patch)
                if grep -q "_findFileRecursive" "$patch_path" 2>/dev/null; then
                    echo "  SKIP: Path lookup fix already applied"
                else
                    # Insert _findFileRecursive after getWikiRoot()
                    sed -i '/getWikiRoot() {/,/return this\.config\.wikiRoot;/{
/return this\.config\.wikiRoot;/a\  }\
  async _findFileRecursive(dir, targetBasename) {\
    if (!await fs5.pathExists(dir)) return null;\
    const entries = await fs5.readdir(dir, { withFileTypes: true });\
    for (const entry of entries) {\
      const fullPath = path5.join(dir, entry.name);\
      if (entry.isDirectory()) {\
        const found = await this._findFileRecursive(fullPath, targetBasename);\
        if (found) return found;\
      } else if (entry.isFile() \&\& entry.name === targetBasename) {\
        return fullPath;\
      }\
    }\
    return null;
                    }' "$patch_path" 2>/dev/null || {
                        echo "  WARN: patch 04 failed via sed, see references/llm-wiki-patches.md"
                        continue
                    }
                    echo "  OK: 04-path-lookup-fix"
                fi
                ;;
        esac
    done
else
    echo "  WARNING: Could not find wiki.js, patches must be manually applied"
    echo "  See references/llm-wiki-patches.md"
fi

# Initialize wiki
echo "[3/4] Initializing wiki at $WIKI_DIR..."
mkdir -p "$WIKI_DIR"
cd "$WIKI_DIR"
wiki init 2>/dev/null || { echo "  Wiki init failed, creating manually..."; mkdir -p raw/untracked raw/ingested wiki/concepts wiki/sources wiki/entities; }

# Configure .wikirc.yaml
echo "[4/4] Configuring .wikirc.yaml..."
if [ -n "$BASE_URL" ] && [ -n "$MODEL" ] && [ -n "$API_KEY" ]; then
    cat > .wikirc.yaml <<YAMLEOF
# LLM Provider Configuration
llm:
  provider: openai
  model: ${MODEL}
  apiKey: ${API_KEY}
  baseUrl: ${BASE_URL}
  temperature: 0.3
  thinking:
    type: disabled
YAMLEOF
    echo "  Configured with provided credentials"
elif [ -f ".wikirc.yaml" ]; then
    echo "  .wikirc.yaml already exists, skipping"
else
    echo "  WARNING: No API credentials provided. Edit .wikirc.yaml manually."
    cat > .wikirc.yaml <<YAMLEOF
# LLM Provider Configuration
llm:
  provider: openai
  model: your-model
  apiKey: YOUR_API_KEY
  baseUrl: https://api.openai.com/v1
  temperature: 0.3
  thinking:
    type: disabled
YAMLEOF
fi

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  cd $WIKI_DIR"
echo "  # Convert & add paper:"
echo "  arxiv2md 2501.11120v1 -o paper.md"
echo "  mkdir -p raw/untracked/2025/01 && mv paper.md raw/untracked/2025/01/"
echo "  wiki ingest \"2025/01/2501.11120v1.md\" -y"
echo ""
echo "  # Query:"
echo "  wiki query \"your question\""
echo ""
echo "  # Helper scripts (from this repo):"
echo "  bash scripts/convert.sh <arxiv_id> [wiki_dir]"
echo "  python3 scripts/bulk-ingest.py [wiki_dir]"
