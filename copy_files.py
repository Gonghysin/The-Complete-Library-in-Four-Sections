import shutil
import os

# --- 配置 ---
SOURCE_DIR = "/Users/mac/主文件夹/新个人文件夹/四库全书归档"
# 目标目录是当前项目下的 'books' 文件夹
DEST_DIR = os.path.join(os.getcwd(), "books") 
# --- 配置结束 ---

def copy_directory_contents(src, dst):
    """    将 src 目录的所有内容复制到 dst 目录。
    如果 dst 不存在，则创建它。
    如果 dst 中的文件/目录与 src 中的同名，则会被覆盖。
    """
    if not os.path.exists(src):
        print(f"错误：源目录 '{src}' 不存在。")
        return False

    try:
        # 如果目标目录存在，并且不是一个目录，则删除它
        if os.path.exists(dst) and not os.path.isdir(dst):
            print(f"目标路径 '{dst}' 已存在且不是目录，正在删除它...")
            os.remove(dst)
        
        # 如果目标目录已存在，先清空它（或者选择其他策略，如合并）
        # 为确保完全复制源目录结构，如果目标目录已是文件夹，先删除再创建
        if os.path.isdir(dst):
            print(f"目标目录 '{dst}' 已存在，正在清空并重新创建...")
            shutil.rmtree(dst)
        
        # 确保目标目录存在
        # shutil.copytree 要求目标目录不能预先存在，所以我们在上面处理了
        # os.makedirs(dst, exist_ok=True) # 这行不再需要，因为 copytree 会创建它

        print(f"正在从 '{src}' 复制到 '{dst}'...")
        # copytree 将递归复制整个目录树
        # dirs_exist_ok=True 选项（Python 3.8+）可以允许目标目录存在并合并内容，
        # 但为了确保是源的精确副本（特别是对于根目录的复制），我们选择先清空目标
        shutil.copytree(src, dst)
        print(f"成功将 '{src}' 复制到 '{dst}'")
        return True
    except Exception as e:
        print(f"复制文件时发生错误：{e}")
        return False

if __name__ == "__main__":
    if not SOURCE_DIR or not os.path.isabs(SOURCE_DIR):
        print(f"错误：源目录 '{SOURCE_DIR}' 未配置或不是绝对路径。请在脚本中修改 SOURCE_DIR。")
    elif not DEST_DIR or not os.path.isabs(DEST_DIR):
        print(f"错误：目标目录 '{DEST_DIR}' 未配置或不是绝对路径。请在脚本中修改 DEST_DIR。")
    else:
        print(f"源目录: {SOURCE_DIR}")
        print(f"目标目录: {DEST_DIR}")
        if copy_directory_contents(SOURCE_DIR, DEST_DIR):
            print("文件复制完成。")
        else:
            print("文件复制失败。") 