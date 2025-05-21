#!/bin/bash

# Shell 脚本：用于复制书籍文件并更新 README 目录

# 设置颜色（可选，用于美化输出）
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 直接切换到项目根目录，确保后续操作路径正确
cd /Users/mac/PycharmProjects/my/The-Complete-Library-in-Four-Sections/ || { echo -e "${RED}无法切换到项目目录，脚本终止。${NC}"; exit 1; }
SCRIPT_DIR="/Users/mac/PycharmProjects/my/The-Complete-Library-in-Four-Sections"

# 使用名为 theenv 的 conda 虚拟环境中的 python
PYTHON_EXECUTABLE="conda run -n theenv python"

COPY_SCRIPT_NAME="copy_files.py"
UPDATE_README_SCRIPT_NAME="update_readme_toc.py"

COPY_SCRIPT_PATH="${SCRIPT_DIR}/${COPY_SCRIPT_NAME}"
UPDATE_README_SCRIPT_PATH="${SCRIPT_DIR}/${UPDATE_README_SCRIPT_NAME}"

# --- 检查 Python 脚本是否存在 ---
if [ ! -f "${COPY_SCRIPT_PATH}" ]; then
    echo -e "${RED}错误：文件复制脚本 '${COPY_SCRIPT_NAME}' 未在 '${SCRIPT_DIR}' 中找到。${NC}"
    exit 1
fi

if [ ! -f "${UPDATE_README_SCRIPT_PATH}" ]; then
    echo -e "${RED}错误：README 更新脚本 '${UPDATE_README_SCRIPT_NAME}' 未在 '${SCRIPT_DIR}' 中找到。${NC}"
    exit 1
fi

# --- 执行文件复制 ---
echo -e "\n${GREEN}>>> 步骤 1: 开始复制文件...${NC}"
${PYTHON_EXECUTABLE} "${COPY_SCRIPT_PATH}"
COPY_EXIT_CODE=$?

if [ ${COPY_EXIT_CODE} -ne 0 ]; then
    echo -e "${RED}文件复制过程中发生错误 (退出码: ${COPY_EXIT_CODE})。请检查上面的输出。${NC}"
    exit 1
else
    echo -e "${GREEN}文件复制成功完成。${NC}"
fi

# --- 执行 README 更新 ---
echo -e "\n${GREEN}>>> 步骤 2: 开始更新 README.md 目录...${NC}"
${PYTHON_EXECUTABLE} "${UPDATE_README_SCRIPT_PATH}"
UPDATE_EXIT_CODE=$?

if [ ${UPDATE_EXIT_CODE} -ne 0 ]; then
    echo -e "${RED}README.md 更新过程中发生错误 (退出码: ${UPDATE_EXIT_CODE})。请检查上面的输出。${NC}"
    exit 1
else
    echo -e "${GREEN}README.md 更新成功完成。${NC}"
fi

# --- 推送到 git 远程仓库 ---
echo -e "\n${GREEN}>>> 步骤 3: 推送更改到 Git 远程仓库...${NC}"

# 添加所有更改
git add .

# 提交更改，自动生成提交信息，包含当前日期时间
COMMIT_MSG="自动更新：同步书籍与目录 ($(date '+%Y-%m-%d %H:%M:%S'))"
git commit -m "${COMMIT_MSG}"

# 推送到远程仓库
GIT_PUSH_OUTPUT=$(git push 2>&1)
PUSH_EXIT_CODE=$?

if [ ${PUSH_EXIT_CODE} -ne 0 ]; then
    echo -e "${RED}推送到 Git 远程仓库时发生错误 (退出码: ${PUSH_EXIT_CODE})。${NC}"
    echo -e "${YELLOW}Git 输出如下：${NC}\n${GIT_PUSH_OUTPUT}"
    exit 1
else
    echo -e "${GREEN}已成功推送到 Git 远程仓库。${NC}"
fi

echo -e "\n${GREEN}所有操作已完成！${NC}" 