import os
import shutil

ROOT = r"c:\industrial-knowledge-platform"
DEST = r"c:\industrial-knowledge-platform\clean_export"

IGNORED_DIRS = {
    "node_modules", "venv", ".venv", "env", "__pycache__", ".pytest_cache", 
    ".mypy_cache", ".next", "dist", "build", "coverage", ".cache", ".idea", 
    ".vscode", "target", ".gradle", "bin", "obj", "logs", "tmp", "temp",
    ".git", ".system_generated", "clean_export", "scratch"
}

IGNORED_EXTS = {
    ".log", ".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe", 
    ".zip", ".tar", ".gz", ".rar"
}

def should_ignore_dir(dname):
    return dname in IGNORED_DIRS

def should_ignore_file(fname):
    ext = os.path.splitext(fname)[1].lower()
    return ext in IGNORED_EXTS

def copy_clean():
    print(f"Starting to copy clean project to {DEST}...")
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
        
    copied_count = 0
    for root, dirs, files in os.walk(ROOT):
        # Filter dirs in-place to avoid walking ignored dirs
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
        
        # Determine the relative path
        rel_path = os.path.relpath(root, ROOT)
        dest_dir = os.path.join(DEST, rel_path)
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        for f in files:
            if not should_ignore_file(f):
                src_file = os.path.join(root, f)
                dest_file = os.path.join(dest_dir, f)
                try:
                    shutil.copy2(src_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    print(f"Failed to copy {src_file}: {e}")

    print(f"Successfully copied {copied_count} files to {DEST}")

if __name__ == "__main__":
    copy_clean()
