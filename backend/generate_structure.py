import os

# List of folder names to exclude
EXCLUDED_DIRS = {"node_modules", "__pycache__", "venv", ".venv", ".pytest_cache", ".git", ".vscode"}

with open("project_structure.txt", "w") as f:
    for root, dirs, files in os.walk("."):
        # Skip any directory that matches an excluded name
        if any(excluded in root.split(os.sep) for excluded in EXCLUDED_DIRS):
            continue
        f.write(f"{root}\n")
        for file in files:
            f.write(f"    {file}\n")