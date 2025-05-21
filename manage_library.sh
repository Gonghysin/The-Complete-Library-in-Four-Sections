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

# --- 步骤 3: 在当前分支提交所有更改 ---
echo -e "\n${GREEN}>>> 步骤 3: 在当前分支提交所有脚本生成和自身的更改...${NC}"

ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}当前操作分支是 '${ORIGINAL_BRANCH}'。${NC}"

echo -e "${YELLOW}正在将所有相关更改添加到 Git 暂存区 (在 '${ORIGINAL_BRANCH}' 分支上)...${NC}"
# 添加由python脚本修改的文件，以及辅助脚本本身
git add README.md "${COPY_SCRIPT_PATH}" "${UPDATE_README_SCRIPT_PATH}" "${SCRIPT_DIR}/manage_library.sh" books/
# 或者更通用地添加所有已更改的受跟踪文件和新文件（如果适用）：
# git add .

if ! git diff --cached --quiet; then
    COMMIT_MESSAGE="自动更新：同步书籍与目录 (在 ${ORIGINAL_BRANCH} 上) ($(date +'%Y-%m-%d %H:%M:%S'))"
    echo -e "${YELLOW}正在提交更改到 '${ORIGINAL_BRANCH}' 分支：'${COMMIT_MESSAGE}'...${NC}"
    git commit -m "${COMMIT_MESSAGE}"
    COMMIT_EXIT_CODE=$?

    if [ ${COMMIT_EXIT_CODE} -ne 0 ]; then
        echo -e "${RED}在 '${ORIGINAL_BRANCH}' 分支上 Git 提交过程中发生错误 (退出码: ${COMMIT_EXIT_CODE})。${NC}"
        exit 1 # 提交失败，关键步骤，退出
    else
        echo -e "${GREEN}更改已成功提交到 '${ORIGINAL_BRANCH}' 分支。${NC}"
    fi
else
    echo -e "${YELLOW}在 '${ORIGINAL_BRANCH}' 分支上没有更改需要提交。${NC}"
fi

# --- 步骤 4: 切换到 main 分支，更新并合并 ---
echo -e "\n${GREEN}>>> 步骤 4: 切换到 'main' 分支，更新并合并 '${ORIGINAL_BRANCH}'...${NC}"

# 切换到 main 分支
echo -e "${YELLOW}正在切换到 'main' 分支...${NC}"
if ! git checkout main; then
    echo -e "${RED}切换到 'main' 分支失败。请确保该分支存在，并且所有更改已在 '${ORIGINAL_BRANCH}' 上提交。${NC}"
    exit 1
fi

# 从远程更新 main 分支
echo -e "${YELLOW}正在从 'origin/main' 更新本地 'main' 分支...${NC}"
if ! git pull origin main; then
    echo -e "${RED}从 'origin/main' 更新本地 'main' 分支失败。可能会导致合并问题，但脚本会继续尝试合并。${NC}"
    # 不在此处退出，允许后续合并尝试，但用户应注意此警告
fi

# 合并原始分支到 main
echo -e "${YELLOW}正在将 '${ORIGINAL_BRANCH}' 分支合并到 'main'...${NC}"
# 使用 --no-ff 确保即使可以快进也创建一个合并提交，便于追踪（可选）
if ! git merge --no-edit "${ORIGINAL_BRANCH}"; then # --no-edit 使用默认合并消息
    echo -e "${RED}将 '${ORIGINAL_BRANCH}' 合并到 'main' 时发生冲突或错误。${NC}"
    echo -e "${YELLOW}请手动解决冲突，然后提交并推送到 'main'。脚本将在此处终止。${NC}"
    # 尝试切回原始分支以方便用户解决冲突
    if [ "${ORIGINAL_BRANCH}" != "main" ]; then
        echo -e "${YELLOW}正在尝试切回原始分支 '${ORIGINAL_BRANCH}'...${NC}"
        git checkout "${ORIGINAL_BRANCH}"
    fi
    exit 1
else
    echo -e "${GREEN}'${ORIGINAL_BRANCH}' 已成功合并到 'main' 分支。${NC}"
fi

# --- 步骤 5: 推送 'main' 分支到远程 ---
echo -e "\n${GREEN}>>> 步骤 5: 推送 'main' 分支到 Git 远程仓库 'origin/main'...${NC}"
if git push origin main; then
    echo -e "${GREEN}'main' 分支已成功推送到 'origin/main'！${NC}"
else
    PUSH_EXIT_CODE=$?
    echo -e "${RED}推送到 'origin/main' 时发生错误 (退出码: ${PUSH_EXIT_CODE})。${NC}"
    echo -e "${RED}请检查 Git 输出以获取详细信息。${NC}"
    # 在此关键步骤失败时，不自动切回分支，让用户在 main 上排查问题
    exit 1
fi

# --- 步骤 6 (可选): 切换回原始分支 ---
if [ "${ORIGINAL_BRANCH}" != "main" ]; then
    echo -e "\n${YELLOW}操作完成，正在尝试切回原始分支 '${ORIGINAL_BRANCH}'...${NC}"
    if ! git checkout "${ORIGINAL_BRANCH}"; then
        echo -e "${YELLOW}无法自动切回分支 '${ORIGINAL_BRANCH}'。您当前仍在 'main' 分支。${NC}"
    else
        echo -e "${GREEN}已成功切回分支 '${ORIGINAL_BRANCH}'。${NC}"
    fi
fi

echo -e "\n${GREEN}所有操作已完成！${NC}" 