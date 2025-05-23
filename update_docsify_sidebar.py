import os
import sys

# --- Configuration ---
# Directory containing the books/notes, relative to the project root
CONTENT_SOURCE_DIR_NAME = "books"
# Docsify's root directory. Empty string means project root.
DOCSIFY_ROOT_DIR_NAME = "" 
# Name of the sidebar file
SIDEBAR_FILENAME = "_sidebar.md"

# Link prefix for sidebar items. Since sidebar is at root and content is in 'books/',
# links will be like "books/topic/file.md"
LINK_PREFIX_FOR_SIDEBAR = CONTENT_SOURCE_DIR_NAME # This will be "books"

# Scanning and exclusion parameters (similar to update_readme_toc.py)
MAX_SCAN_DEPTH = 3
EXCLUSIONS = {".git", ".github", "LICENSE", ".DS_Store"} 
DIR_README_NAME = "README.md" # Standard name for README files in subdirectories
# --- Configuration End ---

def generate_docsify_sidebar_recursive(current_scan_path_abs, # Absolute path of the directory currently being scanned
                                       scan_root_abs,         # Absolute path of the root directory for scanning (e.g., .../books)
                                       base_link_prefix,      # Link prefix (e.g., "../books")
                                       current_depth,         # Current recursion depth
                                       max_depth,             # Max scan depth
                                       exclusions,            # Files/dirs to exclude by name
                                       dir_readme_name):      # Name of README file in directories
    """
    Recursively generates Markdown list items for Docsify sidebar.
    """
    markdown_lines = []
    subdirectories = []
    markdown_files_in_current_dir = []

    try:
        for item_name in sorted(os.listdir(current_scan_path_abs)):
            item_abs_path = os.path.join(current_scan_path_abs, item_name)
            if item_name in exclusions or item_name.startswith('.'):
                continue
            
            if os.path.isdir(item_abs_path):
                subdirectories.append(item_name)
            elif os.path.isfile(item_abs_path):
                if item_name.endswith(".md") and item_name != dir_readme_name:
                    markdown_files_in_current_dir.append(item_name)
    except OSError as e:
        # print(f"Warning: Cannot access directory {current_scan_path_abs}: {e}", file=sys.stderr)
        return []

    indent = "  " * current_depth

    # Process subdirectories first
    for dir_name in subdirectories:
        path_parts_for_link = []
        if base_link_prefix: # Only add if not empty
             path_parts_for_link.append(base_link_prefix)

        if current_scan_path_abs != scan_root_abs:
            path_parts_for_link.extend(os.path.relpath(current_scan_path_abs, scan_root_abs).split(os.sep))
        path_parts_for_link.append(dir_name)
        link_path_for_dir = "/".join(part for part in path_parts_for_link if part != ".")

        readme_in_subdir_path = os.path.join(current_scan_path_abs, dir_name, dir_readme_name)
        if os.path.exists(readme_in_subdir_path):
            markdown_lines.append(f"{indent}- [{dir_name}/]({link_path_for_dir}/{dir_readme_name})")
        else:
            # For Docsify, non-linked directories are usually just titles or skipped.
            # Here, we make them bold text, not a link.
            markdown_lines.append(f"{indent}- {dir_name}/") # Or f"{indent}* {dir_name}/" for bold
        
        if current_depth + 1 < max_depth:
            markdown_lines.extend(generate_docsify_sidebar_recursive(
                os.path.join(current_scan_path_abs, dir_name),
                scan_root_abs,
                base_link_prefix,
                current_depth + 1,
                max_depth,
                exclusions,
                dir_readme_name
            ))

    # Process Markdown files in the current directory
    for file_name in markdown_files_in_current_dir:
        link_text = file_name[:-3] # Remove .md extension for display
        
        path_parts_for_link = []
        if base_link_prefix:
            path_parts_for_link.append(base_link_prefix)
            
        if current_scan_path_abs != scan_root_abs:
             path_parts_for_link.extend(os.path.relpath(current_scan_path_abs, scan_root_abs).split(os.sep))
        path_parts_for_link.append(file_name)
        link_path_for_file = "/".join(part for part in path_parts_for_link if part != ".")

        markdown_lines.append(f"{indent}- [{link_text}]({link_path_for_file})")
        
    return markdown_lines

if __name__ == "__main__":
    project_root = os.getcwd()
    content_scan_dir_abs = os.path.abspath(os.path.join(project_root, CONTENT_SOURCE_DIR_NAME))
    
    # sidebar_file_full_path will be at the project root if DOCSIFY_ROOT_DIR_NAME is empty
    docsify_effective_root_abs = os.path.join(project_root, DOCSIFY_ROOT_DIR_NAME) if DOCSIFY_ROOT_DIR_NAME else project_root
    sidebar_file_full_path = os.path.join(docsify_effective_root_abs, SIDEBAR_FILENAME)

    # If DOCSIFY_ROOT_DIR_NAME is not empty and points to a subdir (e.g. "docs"), ensure it exists.
    # If it's empty (project root), this check is not strictly needed for directory creation.
    if DOCSIFY_ROOT_DIR_NAME: # Only try to create if a subdirectory is specified
        if not os.path.exists(docsify_effective_root_abs):
            try:
                os.makedirs(docsify_effective_root_abs)
                print(f"Created Docsify root directory: '{docsify_effective_root_abs}'")
            except OSError as e:
                print(f"Error: Could not create Docsify root directory '{docsify_effective_root_abs}': {e}", file=sys.stderr)
                sys.exit(1)
        elif not os.path.isdir(docsify_effective_root_abs):
            print(f"Error: Path for Docsify root '{docsify_effective_root_abs}' exists but is not a directory.", file=sys.stderr)
            sys.exit(1)

    sidebar_markdown_lines = []
    if not os.path.isdir(content_scan_dir_abs):
        print(f"Warning: Content source directory '{CONTENT_SOURCE_DIR_NAME}' (i.e., '{content_scan_dir_abs}') not found.", file=sys.stderr)
        sidebar_output_string = "  <!-- Content source directory not found -->"
    else:
        print(f"Generating Docsify sidebar content from '{content_scan_dir_abs}' for '{sidebar_file_full_path}'...")
        sidebar_markdown_lines = generate_docsify_sidebar_recursive(
            current_scan_path_abs=content_scan_dir_abs,
            scan_root_abs=content_scan_dir_abs,
            base_link_prefix=LINK_PREFIX_FOR_SIDEBAR,
            current_depth=0,
            max_depth=MAX_SCAN_DEPTH,
            exclusions=EXCLUSIONS,
            dir_readme_name=DIR_README_NAME
        )
        sidebar_output_string = "\n".join(sidebar_markdown_lines) if sidebar_markdown_lines else ""

    if not sidebar_markdown_lines and os.path.isdir(content_scan_dir_abs):
        sidebar_output_string = "  <!-- No content found for sidebar (directory might be empty or all files excluded) -->"
    
    # For now, we'll just use the generated content.
    final_sidebar_content = "- [Home](/)\n" + sidebar_output_string

    try:
        with open(sidebar_file_full_path, "w", encoding="utf-8") as f:
            f.write(final_sidebar_content)
        print(f"Docsify sidebar successfully written to '{sidebar_file_full_path}'")
        if not final_sidebar_content.strip():
            print(f"(Note: Sidebar is empty or contains only comments)")

    except IOError as e:
        print(f"Error writing Docsify sidebar to '{sidebar_file_full_path}': {e}", file=sys.stderr)
        sys.exit(1) 