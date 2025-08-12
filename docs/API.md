# API Reference

This document lists detected public APIs, functions, classes, and components across the repository. It is generated automatically.


## Python


### `scripts/generate_docs.py`

- **function** `discover_source_files` — `def discover_source_files(root: Path) -> List[Path]:`

```python
from scripts.generate_docs import discover_source_files

result = discover_source_files(# arguments)
print(result)
```

- **function** `read_text_safely` — `def read_text_safely(path: Path) -> str:`

```python
from scripts.generate_docs import read_text_safely

result = read_text_safely(# arguments)
print(result)
```

- **function** `extract_js_ts_exports` — `def extract_js_ts_exports(source: str) -> List[ApiItem]:`

```python
from scripts.generate_docs import extract_js_ts_exports

result = extract_js_ts_exports(# arguments)
print(result)
```

- **function** `extract_python_api` — `def extract_python_api(source: str) -> List[ApiItem]:`

```python
from scripts.generate_docs import extract_python_api

result = extract_python_api(# arguments)
print(result)
```

- **function** `extract_go_api` — `def extract_go_api(source: str) -> List[ApiItem]:`

```python
from scripts.generate_docs import extract_go_api

result = extract_go_api(# arguments)
print(result)
```

- **function** `extract_rust_api` — `def extract_rust_api(source: str) -> List[ApiItem]:`

```python
from scripts.generate_docs import extract_rust_api

result = extract_rust_api(# arguments)
print(result)
```

- **function** `extract_java_api` — `def extract_java_api(source: str) -> List[ApiItem]:`

```python
from scripts.generate_docs import extract_java_api

result = extract_java_api(# arguments)
print(result)
```

- **function** `to_module_path` — `def to_module_path(file_path: Path) -> str:`

```python
from scripts.generate_docs import to_module_path

result = to_module_path(# arguments)
print(result)
```

- **function** `generate_usage_example` — `def generate_usage_example(language: str, file_path: Path, item: ApiItem) -> str:`

```python
from scripts.generate_docs import generate_usage_example

result = generate_usage_example(# arguments)
print(result)
```

- **function** `generate_markdown` — `def generate_markdown(api_map: Dict[str, Dict[Path, List[ApiItem]]]) -> str:`

```python
from scripts.generate_docs import generate_markdown

result = generate_markdown(# arguments)
print(result)
```

- **function** `main` — `def main() -> int:`

```python
from scripts.generate_docs import main

result = main(# arguments)
print(result)
```
