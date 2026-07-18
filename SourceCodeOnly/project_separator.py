import os
import shutil
import json

SOURCE_EXTENSIONS = {
    # Source Code
    '.ts', '.tsx', '.js', '.jsx', '.py', '.java', '.kt', '.cs', '.cpp', '.c', 
    '.h', '.hpp', '.go', '.rs', '.php', '.rb', '.swift', '.sql', '.graphql',
    # Web Files
    '.html', '.css', '.scss', '.sass', '.less',
    # Assets
    '.svg', '.ico', '.ttf', '.woff', '.woff2', '.eot', '.otf', '.png', '.jpg', '.jpeg', '.gif', '.webp'
}

CONFIG_FILES = {
    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'tsconfig.json',
    'dockerfile', 'docker-compose.yml', 'compose.yml', 'compose.yaml', 'requirements.txt',
    'pyproject.toml', 'poetry.lock', 'cargo.toml', 'go.mod', 'go.sum', 'pom.xml',
    'build.gradle', 'settings.gradle', 'gradle.properties', '.gitignore', '.dockerignore'
}

CONFIG_PREFIXES = {
    'next.config.', 'vite.config.', 'tailwind.config.', 'eslint.config.',
    '.eslintrc', '.prettierrc'
}

DOC_EXTENSIONS = {'.md', '.txt'}
DOC_PREFIXES = {'readme', 'license'}
ENV_TEMPLATES = {'.env.example', '.env.template'}

EXCLUDED_DIRS = {
    'node_modules', '.next', 'dist', 'build', 'out', 'coverage', '.cache',
    '.turbo', '.parcel-cache', '.vite', '__pycache__', '.pytest_cache',
    '.venv', 'venv', 'env', 'target', 'bin', 'obj', '.gradle', '.idea',
    '.vscode', 'logs', 'temp', 'tmp', '.git', 'project_source', 'project_excluded'
}

EXCLUDED_EXTS = {
    '.exe', '.dll', '.so', '.dylib', '.zip', '.rar', '.7z', '.tar', '.gz',
    '.log', '.mp4', '.avi', '.mov', '.pt', '.pth', '.bin', '.onnx', '.db', '.sqlite'
}

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

def should_keep_file(filename, filepath, size):
    fname = filename.lower()
    
    # Exclude real .env files
    if fname == '.env' or (fname.startswith('.env.') and fname not in ENV_TEMPLATES):
        return False
        
    # Check max size (unless it's essential config, though configs shouldn't be 25MB)
    if size > MAX_FILE_SIZE:
        return False
        
    # Check extensions
    ext = os.path.splitext(fname)[1]
    if ext in EXCLUDED_EXTS:
        return False
        
    if ext in SOURCE_EXTENSIONS or ext in DOC_EXTENSIONS:
        return True
        
    # Check exact configs
    if fname in CONFIG_FILES or fname in ENV_TEMPLATES:
        return True
        
    # Check prefixes
    for prefix in CONFIG_PREFIXES:
        if fname.startswith(prefix):
            return True
            
    for prefix in DOC_PREFIXES:
        if fname.startswith(prefix):
            return True
            
    # Keep migration/schema files if they match extensions (already covered by .sql/.py)
    # Default to False if not matched, but prompt says "When uncertain, prefer Project_Source."
    # We will exclude things that don't look like source/config at all.
    # To be safe, if it's a small text-like file, maybe keep it. But let's stick to the allowed lists + uncertainty rule.
    # We'll allow unknown files smaller than 1MB just in case, or stick to explicit exclusion.
    # The rule is: "If a file is necessary... keep it. If generated... exclude it. When uncertain, prefer Source."
    # Since we can't know, if it's not explicitly in our known source list, let's keep it IF it's small and not a known binary.
    if size < 1 * 1024 * 1024:
        return True
        
    return False

def main():
    base_dir = r"c:\industrial-knowledge-platform"
    source_dir = os.path.join(base_dir, "Project_Source")
    excluded_dir = os.path.join(base_dir, "Project_Excluded")
    
    if os.path.exists(source_dir):
        shutil.rmtree(source_dir)
    if os.path.exists(excluded_dir):
        shutil.rmtree(excluded_dir)
        
    os.makedirs(source_dir)
    os.makedirs(excluded_dir)
    
    stats = {
        "original_size": 0,
        "source_size": 0,
        "excluded_size": 0,
        "copied_count": 0,
        "excluded_count": 0,
        "dir_sizes": {}
    }
    
    for root, dirs, files in os.walk(base_dir):
        # Exclude destination directories and generated directories
        dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIRS]
        
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            rel_path = ''
            
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                stats["original_size"] += size
            except OSError:
                continue
                
            is_kept = should_keep_file(file, filepath, size)
            
            dest_base = source_dir if is_kept else excluded_dir
            dest_dir = os.path.join(dest_base, rel_path)
            dest_path = os.path.join(dest_dir, file)
            
            os.makedirs(dest_dir, exist_ok=True)
            try:
                shutil.copy2(filepath, dest_path)
                if is_kept:
                    stats["source_size"] += size
                    stats["copied_count"] += 1
                else:
                    stats["excluded_size"] += size
                    stats["excluded_count"] += 1
                    
                    # Track excluded directory sizes
                    if rel_path:
                        top_dir = rel_path.split(os.sep)[0]
                        stats["dir_sizes"][top_dir] = stats["dir_sizes"].get(top_dir, 0) + size
            except Exception as e:
                print(f"Failed to copy {filepath}: {e}")
                
    # Add fully excluded directories to the stats
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':
            continue
            
        top_dir = rel_path.split(os.sep)[0]
        if top_dir.lower() in EXCLUDED_DIRS and top_dir.lower() not in ['project_source', 'project_excluded']:
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    stats["original_size"] += size
                    stats["excluded_size"] += size
                    stats["excluded_count"] += 1
                    stats["dir_sizes"][top_dir] = stats["dir_sizes"].get(top_dir, 0) + size
                    
                    dest_dir = os.path.join(excluded_dir, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(filepath, os.path.join(dest_dir, file))
                except OSError:
                    pass
            # Clear dirs so we don't double count if we walk into them
            
    with open("separation_stats.json", "w") as f:
        json.dump(stats, f)

if __name__ == "__main__":
    main()
