#!/usr/bin/env python3
"""
Code Cleanup Script
Remove unused files and organize the project structure.
"""

import os
import shutil
from pathlib import Path

def create_backup_directory():
    """Create a backup directory for removed files."""
    backup_dir = Path("backup_unused_files")
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def move_to_backup(file_path, backup_dir):
    """Move file to backup directory."""
    if file_path.exists():
        # Create subdirectory structure in backup
        relative_path = file_path.relative_to(Path.cwd())
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(file_path), str(backup_path))
        print(f"Moved {file_path} -> {backup_path}")

def main():
    """Main cleanup function."""
    backup_dir = create_backup_directory()
    project_root = Path.cwd()
    
    # Files currently in use (based on main.py analysis)
    KEEP_UI_FILES = {
        'clean_modern_ui.py',
        'card_layout.py',
        'dashboard.py', 
        'themes.py',
        '__init__.py'
    }
    
    KEEP_DATA_FILES = {
        'stable_fetcher.py',
        'simple_fetcher.py',
        'base.py',
        '__init__.py'
    }
    
    # Remove unused UI files
    ui_dir = project_root / "investment_advisor" / "ui"
    if ui_dir.exists():
        print("\n🧹 Cleaning up UI files...")
        for file_path in ui_dir.iterdir():
            if file_path.is_file() and file_path.name not in KEEP_UI_FILES:
                move_to_backup(file_path, backup_dir)
    
    # Remove unused data fetcher files
    data_dir = project_root / "investment_advisor" / "data"
    if data_dir.exists():
        print("\n🧹 Cleaning up data fetcher files...")
        for file_path in data_dir.iterdir():
            if file_path.is_file() and file_path.name not in KEEP_DATA_FILES:
                move_to_backup(file_path, backup_dir)
    
    # Remove other potentially unused files
    UNUSED_PATTERNS = [
        "investment_advisor/analysis/fundamental.py",  # Not used
        "investment_advisor/analysis/technical.py",   # Not used 
        "investment_advisor/core/mixins.py",          # Not used
        "investment_advisor/core/exceptions.py",      # Not used
        "investment_advisor/core/types.py",           # Not used
        "investment_advisor/visualization/",          # Directory not used
        "investment_advisor/utils/advanced_cache.py", # Not used
        "investment_advisor/utils/json_encoder.py",   # Not used
        "investment_advisor/utils/formatters.py",     # Not used
    ]
    
    print("\n🧹 Cleaning up other unused files...")
    for pattern in UNUSED_PATTERNS:
        path = project_root / pattern
        if path.exists():
            if path.is_file():
                move_to_backup(path, backup_dir)
            elif path.is_dir():
                # Move entire directory
                relative_path = path.relative_to(project_root)
                backup_path = backup_dir / relative_path
                shutil.move(str(path), str(backup_path))
                print(f"Moved directory {path} -> {backup_path}")
    
    print(f"\n✅ Cleanup complete! Unused files moved to {backup_dir}")
    print(f"\n📁 Current project structure:")
    
    # Display cleaned structure
    def show_tree(directory, prefix="", level=0):
        if level > 2:  # Limit depth
            return
        items = sorted([p for p in directory.iterdir() if not p.name.startswith('.')])
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and item.name in ['investment_advisor', 'backend', 'frontend']:
                next_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, next_prefix, level + 1)
    
    show_tree(project_root)

if __name__ == "__main__":
    main()