import os

ROOT = r"c:\industrial-knowledge-platform"

IGNORED_DIRS = {
    "node_modules", "venv", ".venv", "env", "__pycache__", ".pytest_cache", 
    ".mypy_cache", ".next", "dist", "build", "coverage", ".cache", ".idea", 
    ".vscode", "target", ".gradle", "bin", "obj", "logs", "tmp", "temp",
    ".git"
}

IGNORED_EXTS = {
    ".log", ".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe", 
    ".zip", ".tar", ".gz", ".rar"
}

source_files_count = 0
ignored_files_count = 0
found_ignored_dirs = set()

def should_ignore_dir(dname):
    # also ignore .system_generated
    return dname in IGNORED_DIRS or dname == ".system_generated"

def should_ignore_file(fname):
    ext = os.path.splitext(fname)[1].lower()
    return ext in IGNORED_EXTS

tree_lines = []

def walk_tree(dir_path, prefix=""):
    global source_files_count, ignored_files_count
    
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return

    dirs = []
    files = []
    for e in entries:
        full_path = os.path.join(dir_path, e)
        if os.path.isdir(full_path):
            if should_ignore_dir(e):
                found_ignored_dirs.add(e)
                for root, _, fnames in os.walk(full_path):
                    ignored_files_count += len(fnames)
            else:
                dirs.append(e)
        else:
            if should_ignore_file(e):
                ignored_files_count += 1
            else:
                files.append(e)
                source_files_count += 1

    valid_entries = dirs + files
    for i, e in enumerate(valid_entries):
        is_last = (i == len(valid_entries) - 1)
        connector = "└── " if is_last else "├── "
        tree_lines.append(prefix + connector + e)
        
        full_path = os.path.join(dir_path, e)
        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            walk_tree(full_path, prefix + extension)

tree_lines.append(os.path.basename(ROOT))
walk_tree(ROOT)

output = f"""1. Clean project directory tree:

```
{chr(10).join(tree_lines)}
```

2. Total number of source files: {source_files_count}
3. Total ignored files: {ignored_files_count}
4. List of ignored directories: {', '.join(sorted(list(found_ignored_dirs)))}
5. Confirmation that dependency files were excluded: Confirmed. node_modules, venv, and other caches/binaries are successfully excluded.
"""

with open(r"C:\Users\HP\.gemini\antigravity-ide\brain\e1d8647e-64c1-4f1b-bfd9-8938cbebadc5\project_tree.md", "w", encoding="utf-8") as f:
    f.write(output)
