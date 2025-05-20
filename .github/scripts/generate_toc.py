import os
import sys

def generate_dir_md(start_path=".", max_depth=3, exclusions=None, root_readme_name="README.md"):
    """
    Generates a Markdown list representing the directory structure.

    Args:
        start_path (str): The root directory to start scanning from.
        max_depth (int): Maximum depth to scan.
        exclusions (set): A set of directory and file names to exclude.
        root_readme_name (str): The name of the README file in directories (e.g., "README.md").
    """
    if exclusions is None:
        # Default excluded directory and file names (not paths)
        exclusions = {".git", ".github", "LICENSE"} 

    repo_root_abs = os.path.abspath(start_path)
    markdown_output = []

    for current_root_abs, dirs, files in os.walk(repo_root_abs, topdown=True):
        relative_to_repo_root = os.path.relpath(current_root_abs, repo_root_abs)
        
        depth = 0
        if relative_to_repo_root != ".": # Not the start_path itself
            depth = len(relative_to_repo_root.split(os.sep))

        # If max_depth is reached, do not list subdirectories or files from this level further
        # Prune dirs list to prevent os.walk from going deeper
        if depth >= max_depth:
            dirs[:] = [] 
            # We might still want to list files at this max_depth level, so don't 'continue' here.

        # Filter directories
        # Exclude based on name and hidden directories (starting with '.')
        dirs[:] = [d for d in dirs if d not in exclusions and not d.startswith('.')]
        dirs.sort() # Ensure consistent order

        # Filter files
        # Consider only Markdown files and exclude specified names
        md_files = sorted([f for f in files if f.endswith(".md") and f not in exclusions])
        
        indent = "  " * depth

        # List subdirectories (if not exceeding max_depth for the *next* level)
        # The check `depth >= max_depth` above prunes `dirs`, so this loop won't run if already at max_depth.
        # This section lists directories AT the current 'depth'.
        for d_name in dirs: # These are directories at current_root_abs/d_name
            # The link path should be relative to the repo root
            dir_link_path = os.path.join(relative_to_repo_root if relative_to_repo_root != "." else "", d_name).replace("\\", "/")
            
            readme_in_subdir_abs = os.path.join(current_root_abs, d_name, root_readme_name)
            if os.path.exists(readme_in_subdir_abs):
                markdown_output.append(f"{indent}- [{d_name}/]({dir_link_path}/{root_readme_name})")
            else:
                markdown_output.append(f"{indent}- **{d_name}/**")
        
        # List Markdown files at the current depth
        # (unless we are at max_depth and decided not to show files at max_depth, currently we do)
        for f_name in md_files:
            # Special case: do not list the main README.md of the repository in the TOC itself
            if depth == 0 and f_name == root_readme_name and relative_to_repo_root == ".":
                continue

            file_link_path = os.path.join(relative_to_repo_root if relative_to_repo_root != "." else "", f_name).replace("\\", "/")
            link_text = f_name[:-3] # Remove .md extension for display
            markdown_output.append(f"{indent}- [{link_text}]({file_link_path})")
                
    return "\n".join(markdown_output)

if __name__ == "__main__":
    output_file_path = "dir_structure.md" # Default output file name
    
    # Allow specifying output file path via command-line argument
    if len(sys.argv) > 1:
        output_file_path = sys.argv[1]
    
    # Configuration for the script (can be changed as needed)
    scan_path = "."         # Start scanning from the current directory (where the script is run, typically repo root)
    scan_max_depth = 3      # Maximum depth of subdirectories to include
    # Names of README files (e.g. "README.md", "readme.md", etc.)
    main_readme_filename = "README.md" 

    toc_content = generate_dir_md(start_path=scan_path, 
                                  max_depth=scan_max_depth, 
                                  root_readme_name=main_readme_filename)
                                  
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(toc_content)
        # This print is for the GitHub Action log, not for the file content
        # print(f"Generated directory structure in {output_file_path}") 
    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}", file=sys.stderr)
        sys.exit(1) 