"""
Cleanup Script for Temporary Files

This script safely removes temporary directories and files created during
the receipt processing pipeline. It handles nested directories and provides
error handling for safe execution.

Author: HackNJIT 2024 Challenge Team
"""

import os
import sys
from pathlib import Path
from typing import Optional


def cleanup_temp_directory(temp_dir: str, verbose: bool = True) -> bool:
    """
    Recursively remove a temporary directory and all its contents.
    
    Args:
        temp_dir: Path to the temporary directory to clean up
        verbose: If True, print progress messages
        
    Returns:
        True if cleanup was successful, False otherwise
    """
    temp_path = Path(temp_dir)
    
    if not temp_path.exists():
        if verbose:
            print(f"Directory '{temp_dir}' does not exist. Nothing to clean up.")
        return True
    
    if not temp_path.is_dir():
        if verbose:
            print(f"Error: '{temp_dir}' is not a directory.")
        return False
    
    try:
        # Remove all files and subdirectories
        for root, dirs, files in os.walk(temp_path, topdown=False):
            # Remove files first
            for file_name in files:
                file_path = Path(root) / file_name
                try:
                    file_path.unlink()
                    if verbose:
                        print(f"Deleted file: {file_path}")
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}", file=sys.stderr)
                    return False
            
            # Remove subdirectories
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    dir_path.rmdir()
                    if verbose:
                        print(f"Deleted directory: {dir_path}")
                except OSError as e:
                    print(f"Error deleting directory {dir_path}: {e}", file=sys.stderr)
                    return False
        
        # Remove the root directory
        temp_path.rmdir()
        if verbose:
            print(f"Deleted root directory: {temp_path}")
        
        return True
        
    except Exception as e:
        print(f"Unexpected error during cleanup: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for the cleanup script."""
    # Default temporary directory
    temp_dir = os.getenv('TEMP_DIR', 'extracted_stm_files')
    
    print(f"Starting cleanup of temporary directory: {temp_dir}")
    
    success = cleanup_temp_directory(temp_dir)
    
    if success:
        print("✓ Temporary files and directories have been cleaned up successfully.")
        sys.exit(0)
    else:
        print("✗ Cleanup failed. Please check the errors above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
