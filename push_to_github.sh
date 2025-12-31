#!/bin/bash
# ============================================
# 推送代码到 GitHub 脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  推送代码到 GitHub${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查 Git 状态
echo -e "${BLUE}[1/5]${NC} 检查 Git 状态..."
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}⚠ 没有需要提交的更改${NC}"
    echo ""
    echo "未提交的文件："
    git status --short
    echo ""
    read -p "是否继续推送已存在的提交? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
else
    # 添加所有更改
    echo -e "${BLUE}[2/5]${NC} 添加更改到暂存区..."
    git add -A

    # 提交更改
    echo -e "${BLUE}[3/5]${NC} 提交更改..."
    echo ""
    read -p "请输入提交信息 (留空使用默认): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="update: 更新代码 $(date '+%Y-%m-%d %H:%M:%S')"
    fi

    git commit -m "$commit_msg"
    echo -e "${GREEN}✓ 提交完成：$commit_msg${NC}"
fi

# 拉取最新代码
echo ""
echo -e "${BLUE}[4/5]${NC} 拉取远程最新代码..."
git pull origin main --no-edit

# 推送代码
echo ""
echo -e "${BLUE}[5/5]${NC} 推送代码到 GitHub..."
echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  认证方式选择${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "1) 使用 Personal Access Token（推荐）"
echo "2) 使用 SSH Key"
echo "3) 跳过推送"
echo ""
read -p "请选择方式 (1-3): " auth_choice

case $auth_choice in
    1)
        echo ""
        echo -e "${CYAN}使用 Personal Access Token 推送${NC}"
        echo ""
        echo "提示："
        echo "  1. 访问 https://github.com/settings/tokens"
        echo "  2. 生成新的 Personal Access Token"
        echo "  3. 权限选择：repo (完整仓库访问权限)"
        echo "  4. Username: 你的 GitHub 用户名"
        echo "  5. Password: 刚刚生成的 Token"
        echo ""
        git push origin main
        ;;
    2)
        echo ""
        echo -e "${CYAN}使用 SSH Key 推送${NC}"
        echo ""

        # 检查 SSH key
        if [ ! -f ~/.ssh/id_ed25519.pub ] && [ ! -f ~/.ssh/id_rsa.pub ]; then
            echo -e "${YELLOW}⚠ 未找到 SSH Key${NC}"
            read -p "是否生成新的 SSH Key? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ssh-keygen -t ed25519 -C "github@webhook-system" -f ~/.ssh/id_ed25519 -N ""
                echo ""
                echo -e "${GREEN}✓ SSH Key 已生成${NC}"
                echo ""
                echo "公钥内容："
                cat ~/.ssh/id_ed25519.pub
                echo ""
                echo "请将上述公钥添加到 GitHub："
                echo "  https://github.com/settings/keys"
                echo ""
                read -p "添加完成后按 Enter 继续..."
            else
                echo "操作已取消"
                exit 0
            fi
        fi

        # 修改远程 URL 为 SSH
        git remote set-url origin git@github.com:5238717-cell/by.git

        echo -e "${BLUE}正在推送...${NC}"
        git push origin main
        ;;
    3)
        echo "跳过推送"
        exit 0
        ;;
    *)
        echo -e "${RED}无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 推送成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "代码仓库：https://github.com/5238717-cell/by"
echo ""
echo "后续操作："
echo -e "  ${CYAN}1. 在新服务器上克隆代码：${NC}"
echo "     git clone https://github.com/5238717-cell/by.git"
echo ""
echo -e "  ${CYAN}2. 运行一键安装脚本：${NC}"
echo "     cd by && bash install.sh"
echo ""
echo -e "  ${CYAN}3. 启动服务：${NC}"
echo "     ./quick_start.sh"
echo ""
