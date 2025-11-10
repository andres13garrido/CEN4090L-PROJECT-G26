#!/usr/bin/env python

import os
import sys
import shutil
import asyncio
import pathspec
import fnmatch
from typing import Annotated
from mcp.server.fastmcp import FastMCP

# --- Configuration ---

# Create the MCP server instance
mcp = FastMCP(
    "FileSystem-Tools",
    "Provides tools to read, write, list, and manage a local filesystem.",
)

# Default patterns to ignore, used if no .gitignore is found
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    "__pycache__",
    "*.pyc",
    ".venv",
    "venv",
    ".env",
    ".idea",
    ".vscode",
    "*.egg-info",
    "dist",
    "build",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    ".DS_Store",  # macOS
    "Thumbs.db",  # Windows
]

# --- Global State ---
# These will be set at startup in the __main__ block
ROOT_PATH: str | None = None
IGNORE_PATTERNS: pathspec.PathSpec | None = None

# --- Security & Utility Functions ---


def is_safe_path(path: str) -> bool:
    """Check if a path is safely within the ROOT_PATH."""
    if not ROOT_PATH:
        return False  # Server not initialized
    
    # Join root_path and the user-provided path, then get the absolute path
    full_path = os.path.abspath(os.path.join(ROOT_PATH, path))
    
    # Check if the resulting absolute path still starts with the root_path
    return full_path.startswith(ROOT_PATH)


def is_ignored(full_path: str) -> bool:
    """Check if a path matches any ignore patterns."""
    if not ROOT_PATH or not IGNORE_PATTERNS:
        return False  # Server not initialized
    
    # is_ignored needs the path relative to the root
    relative_path = os.path.relpath(full_path, ROOT_PATH)
    return IGNORE_PATTERNS.match_file(relative_path)


# --- MCP Tool Definitions ---


@mcp.tool()
async def list_directory(
    path: Annotated[str, "The directory path to list, relative to the root."] = ".",
    recursive: Annotated[bool, "Whether to list all files recursively."] = False,
) -> str:
    """Lists files and directories at a given path."""
    if not is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."

    full_path = os.path.join(ROOT_PATH, path)
    if not os.path.isdir(full_path):
        return f"Error: Path '{path}' is not a valid directory."

    results = []
    try:
        if recursive:
            for root, dirs, files in os.walk(full_path, topdown=True):
                # Filter ignored directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not is_ignored(os.path.join(root, d))
                ]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if not is_ignored(file_path):
                        results.append(os.path.relpath(file_path, ROOT_PATH))
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    results.append(os.path.relpath(dir_path, ROOT_PATH) + "/")

        else:
            for name in os.listdir(full_path):
                entry_path = os.path.join(full_path, name)
                if is_ignored(entry_path):
                    continue
                
                rel_entry_path = os.path.relpath(entry_path, ROOT_PATH)
                if os.path.isdir(entry_path):
                    results.append(rel_entry_path + "/")
                else:
                    results.append(rel_entry_path)

        return "Directory listing:\n" + "\n".join(sorted(results))
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
async def read_file(
    path: Annotated[str, "The path to the file to read, relative to the root."]
) -> str:
    """Reads the complete content of a specified file."""
    if not is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."

    full_path = os.path.join(ROOT_PATH, path)

    if is_ignored(full_path):
        return f"Error: File '{path}' is in the ignore list."

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return f"Error: File not found at '{path}'."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return f"Error: File '{path}' is not a text file (e.g., binary)."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
async def write_file(
    path: Annotated[str, "The path to the file to write, relative to the root."],
    content: Annotated[str, "The content to write to the file."],
    create_dirs: Annotated[
        bool, "Create parent directories if they don't exist."
    ] = False,
) -> str:
    """Creates or overwrites a file with the specified content."""
    if not is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."

    full_path = os.path.join(ROOT_PATH, path)

    try:
        if create_dirs:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
async def create_directory(
    path: Annotated[str, "The path for the new directory, relative to the root."],
    create_parents: Annotated[
        bool, "Create parent directories if they don't exist (e.g., a/b/c)."
    ] = True,
) -> str:
    """Creates a new directory (folder)."""
    if not is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."

    full_path = os.path.join(ROOT_PATH, path)

    try:
        if create_parents:
            os.makedirs(full_path, exist_ok=True)
        else:
            os.mkdir(full_path)
        return f"Successfully created directory {path}"
    except FileExistsError:
        return f"Error: Directory already exists at '{path}'."
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
async def delete_path(
    path: Annotated[str, "The path to the file or directory to delete."],
    recursive: Annotated[
        bool, "Required to delete non-empty directories."
    ] = False,
) -> str:
    """Deletes a file or directory. Use 'recursive=True' for non-empty folders."""
    if not is_safe_path(path):
        return f"Error: Path '{path}' is outside the allowed directory."

    full_path = os.path.join(ROOT_PATH, path)

    if not os.path.exists(full_path):
        return f"Error: Path not found at '{path}'."

    try:
        if os.path.isdir(full_path):
            if recursive:
                shutil.rmtree(full_path)
            else:
                os.rmdir(full_path)  # Fails if not empty
        else:
            os.remove(full_path)

        return f"Successfully deleted {path}"
    except OSError as e:
        if "Directory not empty" in str(e):
             return f"Error: Directory '{path}' is not empty. Use 'recursive=True' to delete it."
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error deleting: {str(e)}."


@mcp.tool()
async def copy_path(
    source_path: Annotated[str, "The path to the source file or directory."],
    destination_path: Annotated[str, "The path to the destination."],
) -> str:
    """Copies a file or directory to a new location."""
    if not is_safe_path(source_path) or not is_safe_path(destination_path):
        return "Error: Source or destination path is outside root directory."

    full_source = os.path.join(ROOT_PATH, source_path)
    full_dest = os.path.join(ROOT_PATH, destination_path)

    if not os.path.exists(full_source):
        return f"Error: Source path not found at '{source_path}'."

    try:
        if os.path.isdir(full_source):
            shutil.copytree(full_source, full_dest)
        else:
            shutil.copy2(full_source, full_dest)
        return f"Successfully copied {source_path} to {destination_path}"
    except Exception as e:
        return f"Error copying: {str(e)}"

@mcp.tool()
async def move_files_by_pattern(
    file_pattern: Annotated[str, "The glob pattern for files to move (e.g., '*.png')."],
    destination_folder: Annotated[str, "The directory to move the files into."],
    source_path: Annotated[str, "The directory to search in, relative to the root."] = ".",
) -> str:
    """Finds all files matching a pattern in a source directory and moves them to a destination directory."""
    if not is_safe_path(source_path) or not is_safe_path(destination_folder):
        return "Error: Source or destination path is outside the allowed directory."

    full_source_dir = os.path.join(ROOT_PATH, source_path)
    full_dest_dir = os.path.join(ROOT_PATH, destination_folder)

    # Ensure destination exists
    try:
        os.makedirs(full_dest_dir, exist_ok=True)
    except Exception as e:
        return f"Error creating destination directory: {str(e)}"

    moved_files = []
    errors = []

    for root, _, files in os.walk(full_source_dir, topdown=True):
        for file in files:
            if not fnmatch.fnmatch(file, file_pattern):
                continue

            full_file_path = os.path.join(root, file)
            
            # Don't move files that are *already* in the destination folder
            if os.path.commonpath([full_file_path, full_dest_dir]) == full_dest_dir:
                continue

            if is_ignored(full_file_path):
                continue

            try:
                # Construct destination path
                dest_file_path = os.path.join(full_dest_dir, file)
                shutil.move(full_file_path, dest_file_path)
                moved_files.append(os.path.relpath(full_file_path, ROOT_PATH))
            except Exception as e:
                errors.append(f"Failed to move {file}: {str(e)}")

    if not moved_files and not errors:
        return "No files found matching the pattern."
    
    response = ""
    if moved_files:
        response += f"Successfully moved {len(moved_files)} files:\n" + "\n".join(moved_files)
    if errors:
        response += f"\nEncountered {len(errors)} errors:\n" + "\n".join(errors)

    return response.strip()

@mcp.tool()
async def move_path(
    source_path: Annotated[str, "The path to the source file or directory."],
    destination_path: Annotated[str, "The path to the destination."],
) -> str:
    """Moves (renames) a file or directory."""
    if not is_safe_path(source_path) or not is_safe_path(destination_path):
        return "Error: Source or destination path is outside root directory."

    full_source = os.path.join(ROOT_PATH, source_path)
    full_dest = os.path.join(ROOT_PATH, destination_path)

    if not os.path.exists(full_source):
        return f"Error: Source path not found at '{source_path}'."

    try:
        shutil.move(full_source, full_dest)
        return f"Successfully moved {source_path} to {destination_path}"
    except Exception as e:
        return f"Error moving: {str(e)}"


@mcp.tool()
async def search_files(
    query: Annotated[str, "The text to search for (case-insensitive)."],
    file_pattern: Annotated[
        str, "A glob pattern to filter files (e.g., '*.py')."
    ] = "*",
) -> str:
    """Searches for text within files in the directory."""
    global ROOT_PATH, IGNORE_PATTERNS
    results = []
    
    # Use pathspec.Pattern for simple glob matching
    search_pattern = pathspec.Pattern(file_pattern)

    for root, _, files in os.walk(ROOT_PATH):
        for file in files:
            full_path = os.path.join(root, file)

            if is_ignored(full_path):
                continue
                
            if not search_pattern.match_file(file):
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        rel_path = os.path.relpath(full_path, ROOT_PATH)
                        results.append(f"Found in: {rel_path}")
            except (UnicodeDecodeError, IOError):
                continue  # Skip binary files or unreadable files

    if not results:
        return "No matches found."

    return "Search results:\n" + "\n".join(results)


# --- Server Entrypoint ---

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <root_directory>", file=sys.stderr)
        sys.exit(1)

    # Set the global ROOT_PATH
    ROOT_PATH = os.path.abspath(sys.argv[1])

    if not os.path.exists(ROOT_PATH) or not os.path.isdir(ROOT_PATH):
        print(f"Error: Directory does not exist: {ROOT_PATH}", file=sys.stderr)
        sys.exit(1)

    # Initialize ignore patterns
    gitignore_path = os.path.join(ROOT_PATH, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            patterns = f.readlines()
    else:
        patterns = DEFAULT_IGNORE_PATTERNS
    
    # Set the global IGNORE_PATTERNS
    IGNORE_PATTERNS = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    print(
        f"Starting MCP filesystem server in: {ROOT_PATH}",
        file=sys.stderr,
    )
    print(f"Ignoring {len(patterns)} patterns.", file=sys.stderr)

    # Run the server using stdio
    mcp.run(transport="stdio")