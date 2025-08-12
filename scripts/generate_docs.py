#!/usr/bin/env python3

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
OUTPUT_FILE = DOCS_DIR / "API.md"


EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "bin",
    "obj",
    "venv",
    ".venv",
    "__pycache__",
    ".next",
    ".nuxt",
    ".vercel",
    ".cache",
    "coverage",
    ".idea",
    ".vscode",
}

SUPPORTED_EXTENSIONS = {
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".py": "python",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
}


class ApiItem:
    def __init__(self, kind: str, name: str, signature: str, line_number: int):
        self.kind = kind
        self.name = name
        self.signature = signature.strip()
        self.line_number = line_number

    def to_markdown(self) -> str:
        signature_inline = self.signature.replace("`", "\"")
        return f"- **{self.kind}** `{self.name}` — `{signature_inline}`"


def discover_source_files(root: Path) -> List[Path]:
    discovered: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in-place for efficiency
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                discovered.append(file_path)
    return discovered


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# --- Language-specific extractors ---

JS_EXPORT_PATTERNS = [
    ("function", re.compile(r"^\s*export\s+(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(", re.MULTILINE)),
    ("class", re.compile(r"^\s*export\s+class\s+([A-Za-z0-9_$]+)\b", re.MULTILINE)),
    ("const", re.compile(r"^\s*export\s+const\s+([A-Za-z0-9_$]+)\s*=", re.MULTILINE)),
    ("let", re.compile(r"^\s*export\s+let\s+([A-Za-z0-9_$]+)\s*=", re.MULTILINE)),
    ("var", re.compile(r"^\s*export\s+var\s+([A-Za-z0-9_$]+)\s*=", re.MULTILINE)),
    ("type", re.compile(r"^\s*export\s+type\s+([A-Za-z0-9_$]+)\b", re.MULTILINE)),
    ("interface", re.compile(r"^\s*export\s+interface\s+([A-Za-z0-9_$]+)\b", re.MULTILINE)),
    ("enum", re.compile(r"^\s*export\s+enum\s+([A-Za-z0-9_$]+)\b", re.MULTILINE)),
    ("default", re.compile(r"^\s*export\s+default\s+(?:function\s+)?([A-Za-z0-9_$]*)", re.MULTILINE)),
    ("named_export_list", re.compile(r"^\s*export\s*\{([^}]+)\}\s*(?:from\s*['\"][^'\"]+['\"])?:?", re.MULTILINE)),
    ("reexport_all", re.compile(r"^\s*export\s+\*\s+from\s+['\"][^'\"]+['\"];?", re.MULTILINE)),
    ("cjs_object", re.compile(r"module\.exports\s*=\s*\{([^}]+)\}", re.MULTILINE)),
    ("cjs_property", re.compile(r"exports\.([A-Za-z0-9_$]+)\s*=", re.MULTILINE)),
]


def extract_js_ts_exports(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()

    # Helper to capture line number by searching for the matched text
    def find_line_number(match: re.Match) -> int:
        start = match.start()
        upto = source[:start]
        return upto.count("\n") + 1

    for kind, pattern in JS_EXPORT_PATTERNS:
        for m in pattern.finditer(source):
            if kind == "named_export_list":
                names_blob = m.group(1)
                for raw in names_blob.split(','):
                    name = raw.strip()
                    if not name:
                        continue
                    # Handle aliasing: name as alias
                    alias_match = re.match(r"([A-Za-z0-9_$]+)\s+as\s+([A-Za-z0-9_$]+)", name)
                    exported_name = alias_match.group(2) if alias_match else name
                    line_num = find_line_number(m)
                    sig = lines[line_num - 1] if 0 < line_num <= len(lines) else f"export {{ {name} }}"
                    items.append(ApiItem("export", exported_name, sig, line_num))
            elif kind == "reexport_all":
                line_num = find_line_number(m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else "export * from '...'"
                items.append(ApiItem("re-export", "*", sig, line_num))
            elif kind == "cjs_object":
                names_blob = m.group(1)
                for raw in names_blob.split(','):
                    kv = raw.strip().split(':')
                    name = kv[0].strip() if kv else ""
                    if name:
                        line_num = find_line_number(m)
                        sig = lines[line_num - 1] if 0 < line_num <= len(lines) else "module.exports = { ... }"
                        items.append(ApiItem("export", name, sig, line_num))
            elif kind == "cjs_property":
                name = m.group(1)
                line_num = find_line_number(m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else f"exports.{name} = ..."
                items.append(ApiItem("export", name, sig, line_num))
            else:
                name = (m.group(1) or "default").strip()
                if name == "":
                    name = "default"
                line_num = find_line_number(m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else m.group(0)
                items.append(ApiItem(kind, name, sig, line_num))
    return items


PY_PUBLIC_DEF = re.compile(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
PY_PUBLIC_CLASS = re.compile(r"^class\s+([A-Z][a-zA-Z0-9_]*)\s*\(")
PY_ALL_LIST = re.compile(r"__all__\s*=\s*\[([^\]]*)\]")


def extract_python_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        if line.startswith("def "):
            m = PY_PUBLIC_DEF.match(line.strip())
            if m:
                name = m.group(1)
                if not name.startswith("_"):
                    items.append(ApiItem("function", name, line, idx))
        elif line.startswith("class "):
            m = PY_PUBLIC_CLASS.match(line.strip())
            if m:
                name = m.group(1)
                if not name.startswith("_"):
                    items.append(ApiItem("class", name, line, idx))
    # Consider __all__ listing explicit public API
    for m in PY_ALL_LIST.finditer(source):
        names_blob = m.group(1)
        for raw in names_blob.split(','):
            name = raw.strip().strip("'\" ")
            if name and not any(it.name == name for it in items):
                # add as export
                first_line = next((i for i, l in enumerate(lines, start=1) if "__all__" in l), 1)
                items.append(ApiItem("export", name, "__all__", first_line))
    return items


GO_FUNC = re.compile(r"^func\s*(?:\(.*?\)\s*)?([A-Z][A-Za-z0-9_]*)\s*\(")
GO_TYPE = re.compile(r"^type\s+([A-Z][A-Za-z0-9_]*)\s+(?:struct|interface|func|map|\[)")
GO_CONST = re.compile(r"^const\s+([A-Z][A-Za-z0-9_]*)\s*")


def extract_go_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        m = GO_FUNC.match(stripped)
        if m:
            items.append(ApiItem("function", m.group(1), line, idx))
            continue
        m = GO_TYPE.match(stripped)
        if m:
            items.append(ApiItem("type", m.group(1), line, idx))
            continue
        m = GO_CONST.match(stripped)
        if m:
            items.append(ApiItem("const", m.group(1), line, idx))
            continue
    return items


RUST_PUB = re.compile(r"^\s*pub\s+(fn|struct|enum|trait|mod|const)\s+([A-Za-z0-9_]+)")


def extract_rust_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        m = RUST_PUB.match(line)
        if m:
            items.append(ApiItem(m.group(1), m.group(2), line, idx))
    return items


JAVA_PUBLIC_CLASS = re.compile(r"^\s*public\s+(?:abstract\s+|final\s+)?(class|interface|enum)\s+([A-Za-z0-9_]+)")
JAVA_PUBLIC_METHOD = re.compile(r"^\s*public\s+(?:static\s+)?[\w<>,\[\]\s]+\s+([A-Za-z0-9_]+)\s*\(")


def extract_java_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        m = JAVA_PUBLIC_CLASS.match(line)
        if m:
            kind, name = m.group(1), m.group(2)
            items.append(ApiItem(kind, name, line, idx))
            continue
        m = JAVA_PUBLIC_METHOD.match(line)
        if m:
            name = m.group(1)
            items.append(ApiItem("method", name, line, idx))
            continue
    return items


LANGUAGE_EXTRACTORS = {
    "javascript": extract_js_ts_exports,
    "typescript": extract_js_ts_exports,
    "python": extract_python_api,
    "go": extract_go_api,
    "rust": extract_rust_api,
    "java": extract_java_api,
}


def to_module_path(file_path: Path) -> str:
    rel = file_path.relative_to(REPO_ROOT).with_suffix("")
    parts = list(rel.parts)
    # Build python-like dotted path
    dotted = ".".join(parts)
    return dotted


def generate_usage_example(language: str, file_path: Path, item: ApiItem) -> str:
    rel_path_no_ext = file_path.relative_to(REPO_ROOT).with_suffix("")
    module_path = to_module_path(file_path)

    if language in ("javascript", "typescript"):
        ext = "ts" if language == "typescript" else "js"
        if item.kind in {"function", "const", "let", "var", "export"} and item.name != "default":
            return f"```{ext}\nimport {{ {item.name} }} from './{rel_path_no_ext.as_posix()}';\n\nconst result = {item.name}(/* arguments */);\nconsole.log(result);\n```"
        elif item.name == "default":
            return f"```{ext}\nimport Thing from './{rel_path_no_ext.as_posix()}';\n\n// Use the default export\nThing(/* arguments */);\n```"
        elif item.kind == "class":
            return f"```{ext}\nimport {{ {item.name} }} from './{rel_path_no_ext.as_posix()}';\n\nconst instance = new {item.name}(/* constructor args */);\n// instance.method(/* args */)\n```"
        else:
            return f"```{ext}\n// Re-export or type/interface. Import from './{rel_path_no_ext.as_posix()}' as needed.\n```"

    if language == "python":
        if item.kind in {"function", "export"}:
            return f"```python\nfrom {module_path} import {item.name}\n\nresult = {item.name}(# arguments)\nprint(result)\n```"
        if item.kind == "class":
            return f"```python\nfrom {module_path} import {item.name}\n\nobj = {item.name}(# constructor args)\n# obj.method(# args)\n```"
        return "```python\n# Usage example\n```"

    if language == "go":
        return "```go\n// In package usage (import path TBD)\n// result := {name}(/* args */)\n```".replace("{name}", item.name)

    if language == "rust":
        return "```rust\n// use crate::path::to::{name};\n// let result = {name}(/* args */);\n```".replace("{name}", item.name)

    if language == "java":
        if item.kind in {"class", "interface", "enum"}:
            return (
                "```java\n// Example usage\n{ClassName} obj = new {ClassName}();\n// obj.method(/* args */);\n```".replace("{ClassName}", item.name)
            )
        if item.kind == "method":
            return (
                "```java\n// Example invocation (context dependent)\n// new EnclosingClass().{method}(/* args */);\n// or EnclosingClass.{method}(/* args */);\n```".replace("{method}", item.name)
            )
        return "```java\n// Usage example\n```"

    return "```\n// Usage example\n```"


def generate_markdown(api_map: Dict[str, Dict[Path, List[ApiItem]]]) -> str:
    lines: List[str] = []
    lines.append("# API Reference\n")
    lines.append("This document lists detected public APIs, functions, classes, and components across the repository. It is generated automatically.\n")

    total_count = sum(len(items) for lang in api_map.values() for items in lang.values())
    if total_count == 0:
        lines.append("\n> No public APIs detected. Once source files are added, re-run the generator to populate this document.\n")
        return "\n".join(lines)

    # Group by language
    for language, files_map in sorted(api_map.items()):
        # Skip empty languages
        lang_count = sum(len(v) for v in files_map.values())
        if lang_count == 0:
            continue
        lines.append(f"\n## {language.title()}\n")
        for file_path in sorted(files_map.keys(), key=lambda p: p.as_posix()):
            items = files_map[file_path]
            if not items:
                continue
            rel = file_path.relative_to(REPO_ROOT).as_posix()
            lines.append(f"\n### `{rel}`\n")
            for item in items:
                lines.append(item.to_markdown())
                lines.append("")
                lines.append(generate_usage_example(language, file_path, item))
                lines.append("")
    return "\n".join(lines)


def main() -> int:
    source_files = discover_source_files(REPO_ROOT)
    api_map: Dict[str, Dict[Path, List[ApiItem]]] = {}

    for file_path in source_files:
        language = SUPPORTED_EXTENSIONS.get(file_path.suffix.lower())
        if not language:
            continue
        extractor = LANGUAGE_EXTRACTORS[language]
        source_text = read_text_safely(file_path)
        items = extractor(source_text)
        if not items:
            continue
        files_map = api_map.setdefault(language, {})
        files_map[file_path] = items

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    markdown = generate_markdown(api_map)
    OUTPUT_FILE.write_text(markdown, encoding="utf-8")

    print(f"Wrote API reference to {OUTPUT_FILE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())