# Documentation

- API Index: `docs/API.md`
- Full API (single file): `docs/API_FULL.md`
- Per-module pages: `docs/api/<language>/<path>.md`
- Dependency graph: `docs/DIAGRAMS.md` (Mermaid)

## Generate

```bash
python3 scripts/generate_docs.py --format both --verbose
```

Optional flags:
- `--include <regex>`: include only matching paths (repeatable)
- `--exclude <regex>`: exclude matching paths (repeatable)
- `--languages ts,js,python`: limit languages
- `--output-dir ./docs`: change output directory
- `--config ./docsgen.json`: load defaults from JSON file

You can also create `docsgen.json` at repo root:

```json
{
  "include": ["^src/"],
  "exclude": ["\.test\."],
  "languages": "ts,js,python"
}
```