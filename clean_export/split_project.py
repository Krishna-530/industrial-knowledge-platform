import os
import shutil
import time

# --- Config ---
SOURCE_ROOT = r"c:\industrial-knowledge-platform"
DEST_SOURCE = r"c:\Project_Source"
DEST_EXCLUDED = r"c:\Project_Excluded"
REPORT_PATH = r"C:\Users\HP\.gemini\antigravity-ide\brain\e1d8647e-64c1-4f1b-bfd9-8938cbebadc5\summary_report.md"

EXCLUDED_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "out", "coverage", 
    ".cache", ".turbo", ".parcel-cache", ".vite", "__pycache__", ".pytest_cache", 
    ".venv", "venv", "env", "target", "bin", "obj", ".gradle", ".idea", 
    ".vscode", "logs", "temp", "tmp"
}

EXCLUDED_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".db", ".sqlite", ".mp4", ".mov", ".log"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

INCLUDED_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".kt", ".cs", ".cpp", ".c", ".h", ".hpp", 
    ".go", ".rs", ".php", ".rb", ".swift", ".sql", ".graphql", ".html", ".css", ".scss", 
    ".sass", ".less", ".md", ".txt", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot"
}

INCLUDED_EXACT_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "tsconfig.json", 
    "Dockerfile", "docker-compose.yml", "compose.yml", "compose.yaml", "requirements.txt", 
    "pyproject.toml", "poetry.lock", "Cargo.toml", "go.mod", "go.sum", "pom.xml", 
    "build.gradle", "settings.gradle", "gradle.properties", ".gitignore", ".dockerignore",
    ".env.example", ".env.template", "LICENSE"
}

INCLUDED_PREFIXES = {"next.config.", "vite.config.", "tailwind.config.", "eslint.config.", ".eslintrc", ".prettierrc", "README"}

def should_exclude(rel_dir, filename, filepath):
    # 1. Check directories
    parts = rel_dir.replace('\\', '/').split('/')
    for p in parts:
        if p in EXCLUDED_DIRS:
            return True, f"Excluded directory: {p}"
    
    # 2. Check file size
    try:
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE:
            return True, f"File > 25MB ({size} bytes)"
    except Exception:
        pass

    # 3. Check explicit secrets
    if filename.endswith(".env") and filename not in {".env.example", ".env.template"}:
        return True, "Secret (.env)"

    # 4. Check excluded extensions
    ext = os.path.splitext(filename)[1].lower()
    if ext in EXCLUDED_EXTS:
        return True, f"Excluded extension: {ext}"
    
    # 5. Check if it explicitly matches source criteria
    if ext in INCLUDED_EXTS:
        return False, ""
    
    if filename in INCLUDED_EXACT_FILES:
        return False, ""
    
    for prefix in INCLUDED_PREFIXES:
        if filename.startswith(prefix):
            return False, ""
            
    # Keep small UI images like png, jpg, jpeg if not explicitly excluded
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return False, ""

    # Fallback to source when uncertain
    return False, ""

def main():
    print("Starting project split...")
    
    os.makedirs(DEST_SOURCE, exist_ok=True)
    os.makedirs(DEST_EXCLUDED, exist_ok=True)
    
    stats = {
        "orig_size": 0,
        "source_size": 0,
        "excl_size": 0,
        "files_copied": 0,
        "files_excl": 0,
        "largest_excl_dirs": {}
    }

    start_time = time.time()

    for root, dirs, files in os.walk(SOURCE_ROOT):
        # Skip output dirs if they are inside SOURCE_ROOT
        if DEST_SOURCE in root or DEST_EXCLUDED in root:
            continue
            
        rel_dir = os.path.relpath(root, SOURCE_ROOT)
        if rel_dir == ".":
            rel_dir = ""

        for file in files:
            # Skip the script itself
            if file == "split_project.py" and rel_dir == "":
                continue
                
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
            except Exception:
                size = 0
                
            stats["orig_size"] += size
            
            excl, reason = should_exclude(rel_dir, file, filepath)
            
            if excl:
                dest_path = os.path.join(DEST_EXCLUDED, rel_dir, file)
                stats["excl_size"] += size
                stats["files_excl"] += 1
                
                top_level_dir = rel_dir.replace('\\', '/').split('/')[0] if rel_dir else file
                if top_level_dir:
                    stats["largest_excl_dirs"][top_level_dir] = stats["largest_excl_dirs"].get(top_level_dir, 0) + size
            else:
                dest_path = os.path.join(DEST_SOURCE, rel_dir, file)
                stats["source_size"] += size
                stats["files_copied"] += 1
                
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            try:
                shutil.copy2(filepath, dest_path)
            except Exception as e:
                pass # print(f"Error copying {filepath}: {e}")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Project Split Summary Report\n\n")
        f.write(f"**Execution Time**: {round(time.time() - start_time, 2)} seconds\n\n")
        f.write(f"- **Original Project Size**: {stats['orig_size'] / (1024*1024):.2f} MB\n")
        f.write(f"- **Project_Source Size**: {stats['source_size'] / (1024*1024):.2f} MB\n")
        f.write(f"- **Project_Excluded Size**: {stats['excl_size'] / (1024*1024):.2f} MB\n")
        f.write(f"- **Files Copied (Source)**: {stats['files_copied']:,}\n")
        f.write(f"- **Files Excluded**: {stats['files_excl']:,}\n\n")
        
        f.write("## Largest Excluded Directories\n")
        sorted_dirs = sorted(stats["largest_excl_dirs"].items(), key=lambda x: x[1], reverse=True)[:10]
        for d, s in sorted_dirs:
            if s > 0:
                f.write(f"- `{d}`: {s / (1024*1024):.2f} MB\n")
                
    print(f"Complete! Copied {stats['files_copied']} source files. Report generated.")

if __name__ == "__main__":
    main()
