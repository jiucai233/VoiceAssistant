#!/usr/bin/env bash
set -e

# 1. 安装 nvm（Node Version Manager）
echo "安装 nvm..."
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
# 加载 nvm 环境变量
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 2. 使用 nvm 安装 Node.js LTS（即 18+）
echo "安装 Node.js LTS..."
nvm install --lts
nvm use --lts

# 3. 设置 npm 全局包安装目录（无需 sudo）
echo "配置 npm 全局包路径..."
mkdir -p ~/.npm-global
npm config set prefix "$HOME/.npm-global"

# 4. 添加环境变量至 shell 配置文件（兼容 bash/zsh）
RCFILE="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
  RCFILE="$HOME/.zshrc"
fi
grep -qxF 'export PATH="$HOME/.npm-global/bin:$PATH"' "$RCFILE" || \
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> "$RCFILE"
export PATH="$HOME/.npm-global/bin:$PATH"

# 5. 安装 Claude Code CLI（无需 sudo）
echo "安装 Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

# 6. 完成提示和版本验证
echo "安装完成！Node.js、npm 和 Claude Code 已就绪。"
echo "Node 版本：$(node -v)"
echo "npm 版本：$(npm -v)"
echo "Claude Code：$(which claude || echo '未找到 claude 可执行文件')"
