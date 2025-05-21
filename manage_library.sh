#!/bin/bash

# Shell 脚本：用于复制书籍文件并更新 README 目录

# 设置颜色（可选，用于美化输出）
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在的目录，确保我们能找到 Python 脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

PYTHON_EXECUTABLE="python3" # 或者 "python"，取决于您的环境

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

# --- 步骤 3: 提交并推送到 Git 远程仓库 ---
echo -e "\n${GREEN}>>> 步骤 3: 推送更改到 Git 远程仓库...${NC}"

# 首先，将所有已跟踪文件的更改和新文件添加到暂存区
# 特别指定 books 目录，以及脚本和 README
# 使用 git add . 会添加所有未跟踪的文件，这可能是期望的，也可能不是
echo -e "${YELLOW}正在将更改添加到 Git 暂存区...${NC}"
git add README.md "${COPY_SCRIPT_PATH}" "${UPDATE_README_SCRIPT_PATH}" "${SCRIPT_DIR}/manage_library.sh" books/
# 你也可以使用 git add . 来暂存当前目录下所有更改（包括新文件）
# git add .

# 检查是否有东西可以提交
if ! git diff --cached --quiet; then
    COMMIT_MESSAGE="自动更新：同步书籍与目录 ($(date +'%Y-%m-%d %H:%M:%S'))"
    echo -e "${YELLOW}正在提交更改：'${COMMIT_MESSAGE}'...${NC}"
    git commit -m "${COMMIT_MESSAGE}"
    COMMIT_EXIT_CODE=$?

    if [ ${COMMIT_EXIT_CODE} -ne 0 ]; then
        echo -e "${RED}Git 提交过程中发生错误 (退出码: ${COMMIT_EXIT_CODE})。${NC}"
        # exit 1 # 根据需要决定是否在此处退出
    else
        echo -e "${GREEN}更改已成功提交。${NC}"
    fi
else
    echo -e "${YELLOW}没有更改需要提交。${NC}"
fi

# 推送更改
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}当前分支是 '${CURRENT_BRANCH}'。正在尝试推送到远程仓库 'origin'...${NC}"

# 尝试推送，如果失败因为没有上游，则设置上游并推送
if git push origin "${CURRENT_BRANCH}"; then
    echo -e "${GREEN}更改已成功推送到远程仓库！${NC}"
else
    PUSH_EXIT_CODE=$?
    # 检查是否是因为没有上游分支的特定错误
    # (注意：这个检查可能需要根据 git 错误输出的语言和确切文本进行调整)
    # 更简单的方法是直接尝试设置上游
    echo -e "${YELLOW}直接推送失败 (退出码: ${PUSH_EXIT_CODE})。${NC}"
    echo -e "${YELLOW}正在尝试使用 'git push --set-upstream origin ${CURRENT_BRANCH}' 来设置上游并推送...${NC}"
    git push --set-upstream origin "${CURRENT_BRANCH}"
    SETUP_PUSH_EXIT_CODE=$?
    if [ ${SETUP_PUSH_EXIT_CODE} -ne 0 ]; then
        echo -e "${RED}设置上游并推送到 Git 远程仓库时发生错误 (退出码: ${SETUP_PUSH_EXIT_CODE})。${NC}"
        echo -e "${RED}请检查 Git 输出以获取详细信息。如果您不在期望的分支上，请切换分支后重试。${NC}"
        exit 1 # 发生错误，退出脚本
    else
        echo -e "${GREEN}更改已成功推送到远程仓库并设置了上游分支！${NC}"
    fi
fi

echo -e "\n${GREEN}所有操作已完成！${NC}" 