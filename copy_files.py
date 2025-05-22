import shutil
import os
import re

# --- 配置 ---
SOURCE_DIR = "/Users/mac/主文件夹/新个人文件夹/四库全书归档"
# 目标目录是当前项目下的 'books' 文件夹
DEST_DIR = os.path.join(os.getcwd(), "books")
# --- 配置结束 ---

def sanitize_name(name_component):
    """清理文件名或目录名中的特殊字符，替换空格。"""
    # 移除 < 和 >
    sanitized = name_component.replace("<", "")
    sanitized = sanitized.replace(">", "")
    # 将空格替换为连字符
    sanitized = sanitized.replace(" ", "-")
    # 将多个连续的连字符替换为单个连字符
    sanitized = re.sub(r"-+", "-", sanitized)
    # 移除可能出现在开头或结尾的连字符 (例如，如果原名是 "-file-" 或 " file ")
    sanitized = sanitized.strip("-")
    return sanitized

def copy_and_sanitize_directory_contents(src_root, dst_root):
    """
    递归地从 src_root 复制内容到 dst_root，
    并在复制过程中清理文件名和目录名。
    """
    if not os.path.exists(src_root):
        print(f"错误：源目录 '{src_root}' 不存在。")
        return False

    # 确保目标根目录存在，如果存在则清空重建
    if os.path.exists(dst_root):
        if not os.path.isdir(dst_root):
            print(f"目标路径 '{dst_root}' 已存在但不是目录，正在删除并重新创建...")
            os.remove(dst_root)
            os.makedirs(dst_root)
        else:
            print(f"目标目录 '{dst_root}' 已存在，正在清空以进行全新复制...")
            shutil.rmtree(dst_root)
            os.makedirs(dst_root)
    else:
        os.makedirs(dst_root)

    print(f"正在从 '{src_root}' 复制到 '{dst_root}' (同时清理名称)...")

    for src_current_dir, dirs, files in os.walk(src_root):
        # 计算当前源目录相对于 src_root 的路径
        relative_dir_path = os.path.relpath(src_current_dir, src_root)

        # 构建目标目录路径，清理路径中的每个部分
        if relative_dir_path == ".":
            dst_current_dir = dst_root
        else:
            sanitized_parts = [sanitize_name(part) for part in relative_dir_path.split(os.sep)]
            dst_current_dir = os.path.join(dst_root, *sanitized_parts)

        # 创建清理后的目标子目录 (如果不存在)
        if not os.path.exists(dst_current_dir):
            try:
                os.makedirs(dst_current_dir)
            except OSError as e:
                print(f"创建目录 '{dst_current_dir}' 失败: {e}")
                continue # 跳过这个目录

        # 清理并复制文件
        for filename in files:
            original_name_part, extension = os.path.splitext(filename)
            sanitized_filename_part = sanitize_name(original_name_part)
            
            # 避免文件名部分为空的情况
            if not sanitized_filename_part:
                sanitized_filename_part = "untitled" # 或其他占位符

            sanitized_full_filename = sanitized_filename_part + extension
            
            src_file_path = os.path.join(src_current_dir, filename)
            dst_file_path = os.path.join(dst_current_dir, sanitized_full_filename)

            if filename != sanitized_full_filename:
                print(f"  清理复制: '{os.path.join(relative_dir_path, filename) if relative_dir_path != '.' else filename}' -> '{os.path.join(os.path.relpath(dst_current_dir, dst_root), sanitized_full_filename) if os.path.relpath(dst_current_dir, dst_root) != '.' else sanitized_full_filename}'")

            try:
                shutil.copy2(src_file_path, dst_file_path)
            except Exception as e:
                print(f"复制文件 '{src_file_path}' 到 '{dst_file_path}' 时发生错误: {e}")
                # 可选择是否在此处返回 False 或继续

    print(f"成功将 '{src_root}' 的内容复制并清理到 '{dst_root}'")
    return True

if __name__ == "__main__":
    if not SOURCE_DIR or not os.path.isabs(SOURCE_DIR):
        print(f"错误：源目录 '{SOURCE_DIR}' 未配置或不是绝对路径。请在脚本中修改 SOURCE_DIR。")
    elif not DEST_DIR or not os.path.isabs(DEST_DIR):
        print(f"错误：目标目录 '{DEST_DIR}' 未配置或不是绝对路径。请在脚本中修改 DEST_DIR。")
    else:
        print(f"源目录: {SOURCE_DIR}")
        print(f"目标目录: {DEST_DIR}")
        # 使用新的复制和清理函数
        if copy_and_sanitize_directory_contents(SOURCE_DIR, DEST_DIR):
            print("文件复制并清理文件名操作完成。")
        else:
            print("文件复制并清理文件名操作失败。") 