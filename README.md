# aiwebcraft

## Documentation

- Generated API reference: `docs/API.md`
- Regenerate docs:

```bash
python3 scripts/generate_docs.py
```

The generator scans for JS/TS, Python, Go, Rust, and Java sources and documents exported/public APIs with basic usage examples. If no source files exist yet, the generated file will note that nothing was detected.
