# Documentation

- See the generated API reference: `docs/API.md`.
- To regenerate, run:

```bash
python3 scripts/generate_docs.py
```

This scans the repository for supported languages (JS/TS, Python, Go, Rust, Java) and extracts public APIs using lightweight static analysis. If no source files are present, the API reference will indicate that nothing was found.