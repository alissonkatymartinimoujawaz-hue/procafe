#!/usr/bin/env bash
# Renderiza a planilha em PDF para conferencia visual do grafico.
# Uso: ./render_preview.sh caminho/arquivo.xlsx [dir_saida]
set -e
SKILL_DIR=$(echo /root/.claude/skills/synced/*/xlsx/scripts)
python - "$1" "${2:-.}" <<PY
import sys
sys.path.insert(0, "$SKILL_DIR")
from office.soffice import run_soffice
r = run_soffice(["--headless", "--convert-to", "pdf", "--outdir", sys.argv[2], sys.argv[1]], timeout=300)
print(r.stdout, r.stderr)
PY
