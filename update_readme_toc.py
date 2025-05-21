import os
import sys

# --- 配置 ---
# README 文件相对于脚本运行的位置 (通常是项目根目录)
README_FILE_PATH = "README.md"
# 要扫描并生成目录的文件夹 (相对于项目根目录)
CONTENT_DIR_NAME = "books"
# 目录在 README.md 中的标记
START_MARKER = "<!-- AUTO_DIR_START -->"
END_MARKER = "<!-- AUTO_DIR_END -->"
# 扫描的最大深度
MAX_SCAN_DEPTH = 3
# 要排除的目录和文件名 (仅名称，非路径)
EXCLUSIONS = {".git", ".github", "LICENSE", ".DS_Store"} 
# README 文件的标准名称，用于链接到目录的 README
DIR_README_NAME = "README.md"
# --- 配置结束 ---

def generate_markdown_toc_recursive(current_scan_path_abs, # 当前正在扫描的目录的绝对路径
                                  scan_root_abs,         # 扫描的根目录的绝对路径 (e.g., .../books)
                                  base_link_prefix,      # Markdown 链接的前缀 (e.g., "books")
                                  current_depth,         # 当前递归深度
                                  max_depth,             # 最大扫描深度
                                  exclusions,            # 要排除的文件/目录名
                                  dir_readme_name):      # 目录的 README 文件名
    """
    递归地为指定路径生成 Markdown 格式的目录列表。
    """
    markdown_lines = []

    # --- 1. 处理子目录 ---
    subdirectories = []
    # --- 2. 处理文件 ---
    markdown_files_in_current_dir = [] # Markdown 文件，不包括 dir_readme_name

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
        # print(f"警告：无法访问目录 {current_scan_path_abs}: {e}", file=sys.stderr)
        return [] # 返回空列表，表示此路径下无内容或无法访问

    indent = "  " * current_depth

    # 递归处理子目录
    for dir_name in subdirectories:
        # 构建到子目录的链接路径
        # relative_path_from_scan_root = os.path.relpath(os.path.join(current_scan_path_abs, dir_name), scan_root_abs)
        # link_path_for_dir = os.path.join(base_link_prefix, relative_path_from_scan_root).replace("\\", "/")
        
        # 更简洁的链接构建：直接在 base_link_prefix 下构建相对路径
        # current_relative_path_parts = []
        # if current_scan_path_abs != scan_root_abs:
        #     current_relative_path_parts = os.path.relpath(current_scan_path_abs, scan_root_abs).split(os.sep)
        
        path_parts_for_link = [base_link_prefix]
        if current_scan_path_abs != scan_root_abs: # 如果不是在 scan_root (e.g. books/) 下的第一层
            path_parts_for_link.extend(os.path.relpath(current_scan_path_abs, scan_root_abs).split(os.sep))
        path_parts_for_link.append(dir_name)
        link_path_for_dir = "/".join(path_parts_for_link)

        readme_in_subdir_path = os.path.join(current_scan_path_abs, dir_name, dir_readme_name)
        if os.path.exists(readme_in_subdir_path):
            markdown_lines.append(f"{indent}- [{dir_name}/]({link_path_for_dir}/{dir_readme_name})")
        else:
            markdown_lines.append(f"{indent}- **{dir_name}/**")
        
        if current_depth + 1 < max_depth:
            markdown_lines.extend(generate_markdown_toc_recursive(
                os.path.join(current_scan_path_abs, dir_name),
                scan_root_abs,
                base_link_prefix,
                current_depth + 1,
                max_depth,
                exclusions,
                dir_readme_name
            ))

    # 列出当前目录中的 Markdown 文件 (在子目录之后)
    for file_name in markdown_files_in_current_dir:
        link_text = file_name[:-3] # 移除 .md 后缀
        
        path_parts_for_link = [base_link_prefix]
        if current_scan_path_abs != scan_root_abs:
             path_parts_for_link.extend(os.path.relpath(current_scan_path_abs, scan_root_abs).split(os.sep))
        path_parts_for_link.append(file_name)
        link_path_for_file = "/".join(path_parts_for_link)

        markdown_lines.append(f"{indent}- [{link_text}]({link_path_for_file})")
        
    return markdown_lines

def update_readme(readme_path, toc_content, start_marker, end_marker):
    """用新的 TOC 更新 README 文件中标记之间的内容。"""
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误：README 文件 '{readme_path}' 未找到。", file=sys.stderr)
        return False

    new_lines = []
    in_marker_block = False
    start_marker_found = False

    for line in lines:
        if start_marker in line:
            new_lines.append(line) # 保留起始标记行
            if toc_content: # 只有当 toc_content 非空时才添加
                new_lines.append(toc_content + "\n")
            else: # 如果 toc_content 为空 (e.g. books 目录为空或不存在)
                new_lines.append("  <!-- 内容目录为空或无法访问 -->\n")
            in_marker_block = True
            start_marker_found = True
        elif end_marker in line and in_marker_block:
            new_lines.append(line) # 保留结束标记行
            in_marker_block = False
        elif not in_marker_block:
            new_lines.append(line)
    
    if not start_marker_found:
        print(f"错误：未在 '{readme_path}' 中找到起始标记 '{start_marker}'。", file=sys.stderr)
        return False
    if in_marker_block: # 如果找到了开始标记但没找到结束标记
        print(f"错误：未在 '{readme_path}' 中找到结束标记 '{end_marker}' 在起始标记之后。", file=sys.stderr)
        return False

    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"README 文件 '{readme_path}' 已成功更新。")
        return True
    except IOError as e:
        print(f"写入 README 文件 '{readme_path}' 时发生错误: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    project_root = os.getcwd()
    content_scan_dir_abs = os.path.abspath(os.path.join(project_root, CONTENT_DIR_NAME))
    readme_full_path = os.path.join(project_root, README_FILE_PATH)

    if not os.path.isdir(content_scan_dir_abs):
        print(f"警告：内容目录 '{CONTENT_DIR_NAME}' (即 '{content_scan_dir_abs}') 不存在或不是一个目录。", file=sys.stderr)
        toc_markdown_lines = []
    else:
        print(f"正在从 '{content_scan_dir_abs}' 生成目录...")
        toc_markdown_lines = generate_markdown_toc_recursive(
            current_scan_path_abs=content_scan_dir_abs,
            scan_root_abs=content_scan_dir_abs, # 扫描的根也是 content_scan_dir_abs
            base_link_prefix=CONTENT_DIR_NAME,    # 链接以 "books" 开头
            current_depth=0,
            max_depth=MAX_SCAN_DEPTH,
            exclusions=EXCLUSIONS,
            dir_readme_name=DIR_README_NAME
        )
    
    toc_output_string = "\n".join(toc_markdown_lines) if toc_markdown_lines else ""

    if not toc_markdown_lines and os.path.isdir(content_scan_dir_abs):
         # 如果目录存在但没有生成任何内容，则插入提示信息
        toc_output_string = "  <!-- 没有找到可展示的内容 (请检查目录是否为空或文件是否被排除) -->"
    elif not os.path.isdir(content_scan_dir_abs):
        toc_output_string = "  <!-- 内容目录 '/" + CONTENT_DIR_NAME + "' 不存在 -->"

    print("--- 生成的目录预览 ---")
    if toc_output_string.strip():
        print(toc_output_string)
    else:
        print("  (目录为空或无法生成)")
    print("-----------------------")

    if update_readme(readme_full_path, toc_output_string, START_MARKER, END_MARKER):
        print("README 更新成功完成。")
    else:
        print("README 更新失败。") 