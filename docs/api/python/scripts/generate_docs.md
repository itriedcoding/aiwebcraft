# `scripts/generate_docs.py`

## class: `ApiItem`

Signature:

```
class ApiItem
```

Usage:

```python
from scripts.generate_docs import ApiItem

obj = ApiItem(# constructor args)
```

## class: `ModuleDoc`

Signature:

```
class ModuleDoc
```

Usage:

```python
from scripts.generate_docs import ModuleDoc

obj = ModuleDoc(# constructor args)
```

## function: `discover_source_files`

Signature:

```
def discover_source_files(root, include, exclude)
```

Usage:

```python
from scripts.generate_docs import discover_source_files

result = discover_source_files(# arguments)
print(result)
```

## function: `read_text_safely`

Signature:

```
def read_text_safely(path)
```

Usage:

```python
from scripts.generate_docs import read_text_safely

result = read_text_safely(# arguments)
print(result)
```

## function: `extract_js_ts_exports`

Signature:

```
def extract_js_ts_exports(source)
```

Usage:

```python
from scripts.generate_docs import extract_js_ts_exports

result = extract_js_ts_exports(# arguments)
print(result)
```

## function: `extract_python_api`

Signature:

```
def extract_python_api(source)
```

Usage:

```python
from scripts.generate_docs import extract_python_api

result = extract_python_api(# arguments)
print(result)
```

## function: `extract_go_api`

Signature:

```
def extract_go_api(source)
```

Usage:

```python
from scripts.generate_docs import extract_go_api

result = extract_go_api(# arguments)
print(result)
```

## function: `extract_rust_api`

Signature:

```
def extract_rust_api(source)
```

Usage:

```python
from scripts.generate_docs import extract_rust_api

result = extract_rust_api(# arguments)
print(result)
```

## function: `extract_java_api`

Signature:

```
def extract_java_api(source)
```

Usage:

```python
from scripts.generate_docs import extract_java_api

result = extract_java_api(# arguments)
print(result)
```

## function: `to_module_path`

Signature:

```
def to_module_path(file_path)
```

Usage:

```python
from scripts.generate_docs import to_module_path

result = to_module_path(# arguments)
print(result)
```

## function: `generate_usage_example`

Signature:

```
def generate_usage_example(language, file_path, item)
```

Usage:

```python
from scripts.generate_docs import generate_usage_example

result = generate_usage_example(# arguments)
print(result)
```

## function: `resolve_imports`

Signature:

```
def resolve_imports(language, file_path, source)
```

Usage:

```python
from scripts.generate_docs import resolve_imports

result = resolve_imports(# arguments)
print(result)
```

## function: `map_repo_modules`

Signature:

```
def map_repo_modules(files)
```

Usage:

```python
from scripts.generate_docs import map_repo_modules

result = map_repo_modules(# arguments)
print(result)
```

## function: `generate_module_markdown`

Signature:

```
def generate_module_markdown(mod)
```

Usage:

```python
from scripts.generate_docs import generate_module_markdown

result = generate_module_markdown(# arguments)
print(result)
```

## function: `generate_index_markdown`

Signature:

```
def generate_index_markdown(modules, split)
```

Usage:

```python
from scripts.generate_docs import generate_index_markdown

result = generate_index_markdown(# arguments)
print(result)
```

## function: `generate_dependency_mermaid`

Signature:

```
def generate_dependency_mermaid(modules, import_edges)
```

Usage:

```python
from scripts.generate_docs import generate_dependency_mermaid

result = generate_dependency_mermaid(# arguments)
print(result)
```

## function: `module_output_path`

Signature:

```
def module_output_path(mod)
```

Usage:

```python
from scripts.generate_docs import module_output_path

result = module_output_path(# arguments)
print(result)
```

## function: `write_split_docs`

Signature:

```
def write_split_docs(modules, output_dir)
```

Usage:

```python
from scripts.generate_docs import write_split_docs

result = write_split_docs(# arguments)
print(result)
```

## function: `write_single_file`

Signature:

```
def write_single_file(modules, output_file)
```

Usage:

```python
from scripts.generate_docs import write_single_file

result = write_single_file(# arguments)
print(result)
```

## function: `load_config`

Signature:

```
def load_config(config_path)
```

Usage:

```python
from scripts.generate_docs import load_config

result = load_config(# arguments)
print(result)
```

## function: `main`

Signature:

```
def main()
```

Usage:

```python
from scripts.generate_docs import main

result = main(# arguments)
print(result)
```
