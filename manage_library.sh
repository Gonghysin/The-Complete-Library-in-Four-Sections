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

# --- 步骤 3: 准备 Git 分支并提交更改 ---
echo -e "\\n${GREEN}>>> 步骤 3: 准备 Git 分支并提交更改...${NC}"

# 获取当前分支名称，以便之后可以合并
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}当前操作分支是 '${ORIGINAL_BRANCH}'。${NC}"

# 切换到 main 分支
echo -e "${YELLOW}正在切换到 'main' 分支...${NC}"
if ! git checkout main; then
    echo -e "${RED}切换到 'main' 分支失败。请确保该分支存在并且没有未解决的冲突。${NC}"
    exit 1
fi

# 从远程更新 main 分支 (可选，但推荐)
echo -e "${YELLOW}正在从 'origin/main' 更新本地 'main' 分支...${NC}"
if ! git pull origin main; then
    echo -e "${RED}从 'origin/main' 更新本地 'main' 分支失败。${NC}"
    # 根据情况，您可以选择在这里退出或继续
    # exit 1
fi

# 如果原始分支不是 main，并且有意义，则尝试合并原始分支的更改到 main
# 注意：这假设原始分支上的更改是您希望包含在 main 中的。
# 如果 python 脚本的更改是在原始分支上做的，然后我们切换到了 main，
# 文件系统上的更改依然存在，但它们需要被提交到 main 分支。
# 如果原始分支本身有其他未被脚本直接修改但希望同步的提交，则需要合并。
# 对于这个特定场景，因为脚本修改的是工作目录的文件，这些文件更改会直接在 main 分支上被 add 和 commit。
# 所以，除非 ORIGINAL_BRANCH 有独立的、未被脚本触及但需要同步到 main 的提交，否则下面的合并可能不是必须的，
# 或者需要更仔细的策略。
# 为了简化，我们假设所有需要的更改（包括脚本做的）现在都要在 main 上提交。

echo -e "${YELLOW}正在将更改添加到 Git 暂存区 (在 'main' 分支上)...${NC}"
git add README.md "${COPY_SCRIPT_PATH}" "${UPDATE_README_SCRIPT_PATH}" "${SCRIPT_DIR}/manage_library.sh" books/
# git add . # 或者暂存所有更改

if ! git diff --cached --quiet; then
    COMMIT_MESSAGE="自动更新：同步书籍与目录 ($(date +'%Y-%m-%d %H:%M:%S'))"
    echo -e "${YELLOW}正在提交更改到 'main' 分支：'${COMMIT_MESSAGE}'...${NC}"
    git commit -m "${COMMIT_MESSAGE}"
    COMMIT_EXIT_CODE=$?

    if [ ${COMMIT_EXIT_CODE} -ne 0 ]; then
        echo -e "${RED}Git 提交过程中发生错误 (退出码: ${COMMIT_EXIT_CODE})。${NC}"
        # exit 1
    else
        echo -e "${GREEN}更改已成功提交到 'main' 分支。${NC}"
    fi
else
    echo -e "${YELLOW}在 'main' 分支上没有更改需要提交。${NC}"
fi

# --- 步骤 4: 推送 'main' 分支到远程 ---
echo -e "\\n${GREEN}>>> 步骤 4: 推送 'main' 分支到 Git 远程仓库 'origin/main'...${NC}"
if git push origin main; then
    echo -e "${GREEN}'main' 分支已成功推送到 'origin/main'！${NC}"
else
    PUSH_EXIT_CODE=$?
    echo -e "${RED}推送到 'origin/main' 时发生错误 (退出码: ${PUSH_EXIT_CODE})。${NC}"
    echo -e "${RED}请检查 Git 输出以获取详细信息。${NC}"
    # 如果希望在推送失败后切回原分支（可选）
    # if [ "${ORIGINAL_BRANCH}" != "main" ]; then
    #    echo -e "${YELLOW}正在尝试切回原始分支 '${ORIGINAL_BRANCH}'...${NC}"
    #    git checkout "${ORIGINAL_BRANCH}"
    # fi
    exit 1
fi

# （可选）如果原始分支不是 main，并且希望脚本结束后回到原始分支
if [ "${ORIGINAL_BRANCH}" != "main" ]; then
    echo -e "${YELLOW}操作完成，正在尝试切回原始分支 '${ORIGINAL_BRANCH}'...${NC}"
    if ! git checkout "${ORIGINAL_BRANCH}"; then
        echo -e "${YELLOW}无法自动切回分支 '${ORIGINAL_BRANCH}'。您当前仍在 'main' 分支。${NC}"
    else
        echo -e "${GREEN}已成功切回分支 '${ORIGINAL_BRANCH}'。${NC}"
    fi
fi

echo -e "\n${GREEN}所有操作已完成！${NC}" 