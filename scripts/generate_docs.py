#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs"
DEFAULT_SINGLE_FILE = DEFAULT_OUTPUT_DIR / "API.md"
DEFAULT_INDEX_FILE = DEFAULT_OUTPUT_DIR / "README.md"
SPLIT_OUTPUT_BASE = DEFAULT_OUTPUT_DIR / "api"
DIAGRAMS_FILE = DEFAULT_OUTPUT_DIR / "DIAGRAMS.md"
CONFIG_FILES = [REPO_ROOT / "docsgen.json", REPO_ROOT / ".docsgen.json"]

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

IMPORT_PATTERNS = {
    "javascript": [
        re.compile(r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"];?", re.MULTILINE),
        re.compile(r"^\s*const\s+.*?=\s*require\(['\"]([^'\"]+)['\"]\)\s*;?", re.MULTILINE),
        re.compile(r"^\s*export\s+\*\s+from\s+['\"]([^'\"]+)['\"];?", re.MULTILINE),
    ],
    "typescript": [
        re.compile(r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"];?", re.MULTILINE),
        re.compile(r"^\s*const\s+.*?=\s*require\(['\"]([^'\"]+)['\"]\)\s*;?", re.MULTILINE),
        re.compile(r"^\s*export\s+\*\s+from\s+['\"]([^'\"]+)['\"];?", re.MULTILINE),
    ],
    "python": [
        re.compile(r"^\s*from\s+([\w\.]+)\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+([\w\.]+)", re.MULTILINE),
    ],
}


@dataclass
class ApiItem:
    kind: str
    name: str
    signature: str
    line_number: int
    description: Optional[str] = None

    def to_markdown(self) -> str:
        signature_inline = self.signature.replace("`", "\"").strip()
        desc = f" — {self.description.strip()}" if self.description else ""
        return f"- **{self.kind}** `{self.name}` — `{signature_inline}`{desc}"


@dataclass
class ModuleDoc:
    language: str
    file_path: Path
    items: List[ApiItem]


# --- Discovery ---

def discover_source_files(root: Path, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> List[Path]:
    include = include or []
    exclude = exclude or []
    discovered: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            file_path = Path(dirpath) / filename
            suffix = file_path.suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                continue
            rel = file_path.relative_to(root).as_posix()
            # include/exclude filters
            if include and not any(re.search(p, rel) for p in include):
                continue
            if exclude and any(re.search(p, rel) for p in exclude):
                continue
            discovered.append(file_path)
    return discovered


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# --- Language-specific extraction ---

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


def _find_line_number(source: str, match: re.Match) -> int:
    start = match.start()
    return source.count("\n", 0, start) + 1


def _extract_jsdoc_before(source: str, start_line: int) -> Optional[str]:
    # Find nearest /** ... */ or consecutive // lines immediately above the start_line
    lines = source.splitlines()
    idx = start_line - 2  # 0-based index, line above declaration
    # First check block comment
    block = []
    while idx >= 0:
        line = lines[idx].rstrip()
        if line.strip().endswith("*/"):
            # Walk backwards to find beginning
            block.append(line)
            idx2 = idx - 1
            found_start = False
            while idx2 >= 0:
                line2 = lines[idx2].rstrip()
                block.append(line2)
                if line2.strip().startswith("/**"):
                    found_start = True
                    break
                idx2 -= 1
            if found_start:
                block.reverse()
                text = "\n".join(block)
                content = re.sub(r"^\s*/\*\*?|\*/\s*$|^\s*\*\s?", "", text, flags=re.MULTILINE).strip()
                return content or None
            else:
                break
        if line.strip() == "":
            idx -= 1
            continue
        break
    # Then check consecutive // lines
    idx = start_line - 2
    slash_lines: List[str] = []
    while idx >= 0:
        line = lines[idx].rstrip()
        if line.strip().startswith("//"):
            slash_lines.append(line)
            idx -= 1
            continue
        if line.strip() == "":
            idx -= 1
            continue
        break
    if slash_lines:
        slash_lines.reverse()
        content = "\n".join(l.strip().lstrip("//").strip() for l in slash_lines).strip()
        return content or None
    return None


def _is_react_component(source: str, name: str) -> bool:
    # Heuristics: PascalCase name and function/const assigned to arrow that returns JSX
    if not name or not name[0].isupper():
        return False
    pattern_func = re.compile(rf"\bfunction\s+{re.escape(name)}\b[\s\S]*?return\s*\(\s*<", re.MULTILINE)
    pattern_const_arrow = re.compile(rf"\b{re.escape(name)}\s*=\s*\(.*?\)\s*=>[\s\S]*?return\s*\(\s*<", re.MULTILINE)
    pattern_type = re.compile(rf"\b{re.escape(name)}\s*:\s*React\.FC|JSX\.Element|ReactElement")
    return bool(pattern_func.search(source) or pattern_const_arrow.search(source) or pattern_type.search(source))


def extract_js_ts_exports(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for kind, pattern in JS_EXPORT_PATTERNS:
        for m in pattern.finditer(source):
            if kind == "named_export_list":
                names_blob = m.group(1)
                for raw in names_blob.split(','):
                    name = raw.strip()
                    if not name:
                        continue
                    alias_match = re.match(r"([A-Za-z0-9_$]+)\s+as\s+([A-Za-z0-9_$]+)", name)
                    exported_name = alias_match.group(2) if alias_match else name
                    line_num = _find_line_number(source, m)
                    sig = lines[line_num - 1] if 0 < line_num <= len(lines) else f"export {{ {name} }}"
                    desc = _extract_jsdoc_before(source, line_num)
                    resolved_kind = "component" if _is_react_component(source, exported_name) else "export"
                    items.append(ApiItem(resolved_kind, exported_name, sig, line_num, desc))
            elif kind == "reexport_all":
                line_num = _find_line_number(source, m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else "export * from '...'"
                desc = _extract_jsdoc_before(source, line_num)
                items.append(ApiItem("re-export", "*", sig, line_num, desc))
            elif kind == "cjs_object":
                names_blob = m.group(1)
                for raw in names_blob.split(','):
                    kv = raw.strip().split(':')
                    name = kv[0].strip() if kv else ""
                    if name:
                        line_num = _find_line_number(source, m)
                        sig = lines[line_num - 1] if 0 < line_num <= len(lines) else "module.exports = { ... }"
                        desc = _extract_jsdoc_before(source, line_num)
                        resolved_kind = "component" if _is_react_component(source, name) else "export"
                        items.append(ApiItem(resolved_kind, name, sig, line_num, desc))
            elif kind == "cjs_property":
                name = m.group(1)
                line_num = _find_line_number(source, m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else f"exports.{name} = ..."
                desc = _extract_jsdoc_before(source, line_num)
                resolved_kind = "component" if _is_react_component(source, name) else "export"
                items.append(ApiItem(resolved_kind, name, sig, line_num, desc))
            else:
                name = (m.group(1) or "default").strip()
                if name == "":
                    name = "default"
                line_num = _find_line_number(source, m)
                sig = lines[line_num - 1] if 0 < line_num <= len(lines) else m.group(0)
                desc = _extract_jsdoc_before(source, line_num)
                resolved_kind = "component" if _is_react_component(source, name) else kind
                items.append(ApiItem(resolved_kind, name, sig, line_num, desc))
    return items


# Python via AST to get accurate docstrings and parameters

def extract_python_api(source: str) -> List[ApiItem]:
    try:
        import ast
    except Exception:
        return []
    items: List[ApiItem] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return items

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: "ast.FunctionDef") -> None:
            if node.name.startswith("_"):
                return
            doc = ast.get_docstring(node)
            args = [a.arg for a in node.args.args]
            sig = f"def {node.name}({', '.join(args)})"
            items.append(ApiItem("function", node.name, sig, getattr(node, "lineno", 1), doc))

        def visit_AsyncFunctionDef(self, node: "ast.AsyncFunctionDef") -> None:
            if node.name.startswith("_"):
                return
            doc = ast.get_docstring(node)
            args = [a.arg for a in node.args.args]
            sig = f"async def {node.name}({', '.join(args)})"
            items.append(ApiItem("function", node.name, sig, getattr(node, "lineno", 1), doc))

        def visit_ClassDef(self, node: "ast.ClassDef") -> None:
            if node.name.startswith("_"):
                return
            doc = ast.get_docstring(node)
            bases = [getattr(b, 'id', getattr(getattr(b, 'attr', None), '__str__', lambda: '')()) for b in node.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            sig = f"class {node.name}{base_str}"
            items.append(ApiItem("class", node.name, sig, getattr(node, "lineno", 1), doc))

    Visitor().visit(tree)

    # __all__ explicit exports
    try:
        m = re.search(r"__all__\s*=\s*\[([^\]]*)\]", source)
        if m:
            for raw in m.group(1).split(','):
                name = raw.strip().strip("'\" ")
                if name and not any(it.name == name for it in items):
                    items.append(ApiItem("export", name, "__all__", 1, None))
    except Exception:
        pass

    return items


# Go public declarations and preceding comments
GO_FUNC = re.compile(r"^func\s*(?:\(.*?\)\s*)?([A-Z][A-Za-z0-9_]*)\s*\(")
GO_TYPE = re.compile(r"^type\s+([A-Z][A-Za-z0-9_]*)\s+(?:struct|interface|func|map|\[)")
GO_CONST = re.compile(r"^const\s+([A-Z][A-Za-z0-9_]*)\s*")


def _extract_line_comments_before(source: str, start_line: int, markers: Tuple[str, ...]) -> Optional[str]:
    lines = source.splitlines()
    idx = start_line - 2
    comment_lines: List[str] = []
    while idx >= 0:
        stripped = lines[idx].strip()
        if any(stripped.startswith(m) for m in markers):
            c = stripped
            for m in markers:
                if c.startswith(m):
                    c = c[len(m):]
                    break
            comment_lines.append(c.strip())
            idx -= 1
            continue
        if stripped == "":
            idx -= 1
            continue
        break
    if comment_lines:
        comment_lines.reverse()
        return "\n".join(comment_lines).strip() or None
    return None


def extract_go_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        m = GO_FUNC.match(stripped)
        if m:
            doc = _extract_line_comments_before(source, idx, ("//",))
            items.append(ApiItem("function", m.group(1), line, idx, doc))
            continue
        m = GO_TYPE.match(stripped)
        if m:
            doc = _extract_line_comments_before(source, idx, ("//",))
            items.append(ApiItem("type", m.group(1), line, idx, doc))
            continue
        m = GO_CONST.match(stripped)
        if m:
            doc = _extract_line_comments_before(source, idx, ("//",))
            items.append(ApiItem("const", m.group(1), line, idx, doc))
            continue
    return items


# Rust
RUST_PUB = re.compile(r"^\s*pub\s+(fn|struct|enum|trait|mod|const)\s+([A-Za-z0-9_]+)")


def extract_rust_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        m = RUST_PUB.match(line)
        if m:
            # Extract doc comments (/// or /** */)
            block_doc = _extract_jsdoc_before(source, idx)
            line_doc = _extract_line_comments_before(source, idx, ("///",))
            doc = block_doc or line_doc
            items.append(ApiItem(m.group(1), m.group(2), line, idx, doc))
    return items


# Java
JAVA_PUBLIC_CLASS = re.compile(r"^\s*public\s+(?:abstract\s+|final\s+)?(class|interface|enum)\s+([A-Za-z0-9_]+)")
JAVA_PUBLIC_METHOD = re.compile(r"^\s*public\s+(?:static\s+)?[\w<>,\[\]\s]+\s+([A-Za-z0-9_]+)\s*\(")


def extract_java_api(source: str) -> List[ApiItem]:
    items: List[ApiItem] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        m = JAVA_PUBLIC_CLASS.match(line)
        if m:
            doc = _extract_jsdoc_before(source, idx)
            kind, name = m.group(1), m.group(2)
            items.append(ApiItem(kind, name, line, idx, doc))
            continue
        m = JAVA_PUBLIC_METHOD.match(line)
        if m:
            doc = _extract_jsdoc_before(source, idx)
            name = m.group(1)
            items.append(ApiItem("method", name, line, idx, doc))
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
    return ".".join(rel.parts)


def generate_usage_example(language: str, file_path: Path, item: ApiItem) -> str:
    rel_path_no_ext = file_path.relative_to(REPO_ROOT).with_suffix("")
    module_path = to_module_path(file_path)

    if language in ("javascript", "typescript"):
        ext = "ts" if language == "typescript" else "js"
        if item.kind == "component":
            return f"```{ext}\nimport {{ {item.name} }} from './{rel_path_no_ext.as_posix()}';\n\n<{item.name} /* props */ />\n```"
        if item.kind in {"function", "const", "let", "var", "export"} and item.name != "default":
            return f"```{ext}\nimport {{ {item.name} }} from './{rel_path_no_ext.as_posix()}';\n\nconst result = {item.name}(/* arguments */);\nconsole.log(result);\n```"
        if item.name == "default":
            return f"```{ext}\nimport Thing from './{rel_path_no_ext.as_posix()}';\n\nThing(/* arguments */);\n```"
        if item.kind == "class":
            return f"```{ext}\nimport {{ {item.name} }} from './{rel_path_no_ext.as_posix()}';\n\nconst instance = new {item.name}(/* constructor args */);\n```"
        return f"```{ext}\n// Import types or re-exports from './{rel_path_no_ext.as_posix()}'\n```"

    if language == "python":
        if item.kind in {"function", "export"}:
            return f"```python\nfrom {module_path} import {item.name}\n\nresult = {item.name}(# arguments)\nprint(result)\n```"
        if item.kind == "class":
            return f"```python\nfrom {module_path} import {item.name}\n\nobj = {item.name}(# constructor args)\n```"
        return "```python\n# Usage example\n```"

    if language == "go":
        return "```go\n// In package usage (import path TBD)\n// result := {name}(/* args */)\n```".replace("{name}", item.name)

    if language == "rust":
        return "```rust\n// use crate::path::to::{name};\n// let result = {name}(/* args */);\n```".replace("{name}", item.name)

    if language == "java":
        if item.kind in {"class", "interface", "enum"}:
            return (
                "```java\n// Example usage\n{ClassName} obj = new {ClassName}();\n```".replace("{ClassName}", item.name)
            )
        if item.kind == "method":
            return (
                "```java\n// new EnclosingClass().{method}(/* args */);\n```".replace("{method}", item.name)
            )
        return "```java\n// Usage example\n```"

    return "```\n// Usage example\n```"


# Import graph

def resolve_imports(language: str, file_path: Path, source: str) -> Set[str]:
    modules: Set[str] = set()
    patterns = IMPORT_PATTERNS.get(language)
    if not patterns:
        return modules
    for pat in patterns:
        for m in pat.finditer(source):
            mod = m.group(1)
            modules.add(mod)
    return modules


def map_repo_modules(files: List[Path]) -> Dict[str, Path]:
    # Map probable import specifiers to file paths (for intra-repo edges)
    mapping: Dict[str, Path] = {}
    for fp in files:
        rel = fp.relative_to(REPO_ROOT)
        # JS/TS import without extension
        mapping[rel.with_suffix("").as_posix()] = fp
        # Python dotted
        mapping[".".join(rel.with_suffix("").parts)] = fp
    return mapping


# --- Output generation ---

def generate_module_markdown(mod: ModuleDoc) -> str:
    lines: List[str] = []
    rel = mod.file_path.relative_to(REPO_ROOT).as_posix()
    lines.append(f"# `{rel}`\n")
    for item in mod.items:
        lines.append(f"## {item.kind}: `{item.name}`\n")
        if item.description:
            lines.append(item.description + "\n")
        lines.append("Signature:\n")
        lines.append(f"```\n{item.signature}\n```\n")
        lines.append("Usage:\n")
        lines.append(generate_usage_example(mod.language, mod.file_path, item) + "\n")
    return "\n".join(lines)


def generate_index_markdown(modules: List[ModuleDoc], split: bool) -> str:
    lines: List[str] = []
    lines.append("# API Reference\n")
    lines.append("Auto-generated documentation of public APIs, functions, classes, and components.\n")
    counts: Dict[str, int] = {}
    for m in modules:
        counts[m.language] = counts.get(m.language, 0) + len(m.items)
    if not modules:
        lines.append("\n> No public APIs detected.\n")
        return "\n".join(lines)
    lines.append("\n## Summary\n")
    for lang, cnt in sorted(counts.items()):
        lines.append(f"- {lang.title()}: {cnt} items")
    lines.append("\n## Modules\n")
    for m in sorted(modules, key=lambda x: x.file_path.as_posix()):
        rel = m.file_path.relative_to(REPO_ROOT).as_posix()
        if split:
            out_rel = module_output_path(m).relative_to(DEFAULT_OUTPUT_DIR).as_posix()
            lines.append(f"- `{rel}` — see [{out_rel}]({out_rel})")
        else:
            lines.append(f"- `{rel}`")
    return "\n".join(lines)


def generate_dependency_mermaid(modules: List[ModuleDoc], import_edges: List[Tuple[Path, Path]]) -> str:
    lines: List[str] = []
    lines.append("# Dependency Graph\n")
    lines.append("This graph shows intra-repository imports between documented modules.\n")
    lines.append("\n```mermaid\n")
    lines.append("graph LR")
    # Map nodes to ids
    node_ids: Dict[Path, str] = {}
    for idx, m in enumerate(modules):
        node_ids[m.file_path] = f"N{idx}"
    for m in modules:
        nid = node_ids[m.file_path]
        label = m.file_path.relative_to(REPO_ROOT).as_posix()
        lines.append(f"  {nid}[\"{label}\"]")
    for a, b in import_edges:
        if a in node_ids and b in node_ids:
            lines.append(f"  {node_ids[a]} --> {node_ids[b]}")
    lines.append("```\n")
    return "\n".join(lines)


def module_output_path(mod: ModuleDoc) -> Path:
    rel = mod.file_path.relative_to(REPO_ROOT)
    return SPLIT_OUTPUT_BASE / mod.language / rel.with_suffix(".md")


def write_split_docs(modules: List[ModuleDoc], output_dir: Path) -> None:
    for mod in modules:
        out_path = module_output_path(mod)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(generate_module_markdown(mod), encoding="utf-8")


def write_single_file(modules: List[ModuleDoc], output_file: Path) -> None:
    lines: List[str] = []
    lines.append(generate_index_markdown(modules, split=False))
    for mod in sorted(modules, key=lambda m: m.file_path.as_posix()):
        lines.append("\n---\n")
        lines.append(generate_module_markdown(mod))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")


# --- CLI and main ---

def load_config(config_path: Optional[Path]) -> Dict:
    paths = [config_path] if config_path else CONFIG_FILES
    for p in paths:
        if p and p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate API documentation for the repository.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory (default: docs)")
    parser.add_argument("--format", choices=["single", "split", "both"], default="both", help="Output format")
    parser.add_argument("--include", action="append", help="Regex to include paths (can be repeated)")
    parser.add_argument("--exclude", action="append", help="Regex to exclude paths (can be repeated)")
    parser.add_argument("--languages", help="Comma-separated languages to scan (default: all)")
    parser.add_argument("--config", type=Path, help="Path to JSON config file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    config = load_config(args.config)

    include = args.include or config.get("include") or []
    exclude = args.exclude or config.get("exclude") or []
    languages = set([l.strip().lower() for l in (args.languages or config.get("languages", "")).split(",") if l.strip()])

    files = discover_source_files(REPO_ROOT, include=include, exclude=exclude)
    if languages:
        files = [f for f in files if SUPPORTED_EXTENSIONS.get(f.suffix.lower()) in languages]

    if args.verbose:
        print(f"Discovered {len(files)} files")

    api_modules: List[ModuleDoc] = []
    import_edges: List[Tuple[Path, Path]] = []
    repo_map = map_repo_modules(files)

    for fp in files:
        lang = SUPPORTED_EXTENSIONS.get(fp.suffix.lower())
        if not lang:
            continue
        src = read_text_safely(fp)
        extractor = LANGUAGE_EXTRACTORS[lang]
        items = extractor(src)
        if not items:
            continue
        api_modules.append(ModuleDoc(lang, fp, items))
        # Resolve imports for graph
        for spec in resolve_imports(lang, fp, src):
            # Try to resolve to repo file
            candidates = []
            if spec.startswith("."):
                # relative import path for JS/TS
                resolved = (fp.parent / spec).resolve()
                # Try with and without extensions, index files are ignored for simplicity
                for ext in ("", ".ts", ".tsx", ".js", ".jsx", ".py"):
                    cand = (resolved.with_suffix(ext)) if ext else resolved
                    if cand in files:
                        candidates.append(cand)
            else:
                # Absolute-like: look up in mapping
                if spec in repo_map:
                    candidates.append(repo_map[spec])
            for c in candidates:
                import_edges.append((fp, c))

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write index
    index_md = generate_index_markdown(api_modules, split=(args.format in ("split", "both")))
    (output_dir / "API.md").write_text(index_md, encoding="utf-8")

    # Write formats
    if args.format in ("split", "both"):
        write_split_docs(api_modules, output_dir)
    if args.format in ("single", "both"):
        write_single_file(api_modules, output_dir / "API_FULL.md")

    # Dependency graph
    diagrams_md = generate_dependency_mermaid(api_modules, import_edges)
    (output_dir / "DIAGRAMS.md").write_text(diagrams_md, encoding="utf-8")

    if args.verbose:
        print(f"Wrote docs to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())