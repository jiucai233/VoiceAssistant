#!/usr/bin/env bash
set -e

echo "[1/5] 检查 Python 环境..."
if ! command -v python3 >/dev/null; then
  echo "Error: 需要 python3，但未检测到"
  exit 1
fi

echo "[2/5] 安装 pip（如缺失）..."
python3 -m ensurepip --upgrade || true
python3 -m pip install --user --upgrade pip

echo "[3/5] 安装 gemini-cli 到用户目录..."
python3 -m pip install --user --upgrade gemini-cli

echo "[4/5] 确保 ~/.local/bin 在 PATH 中..."
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then SHELL_RC="$HOME/.zshrc"; fi
grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
export PATH="$HOME/.local/bin:$PATH"

echo "[5/5] 验证安装..."
command -v gemini >/dev/null && echo "✅ 安装成功！可以使用 \`gemini\` 命令了" || echo "❌ 安装失败，PATH 未配置正确"

echo
echo "👉 首次使用请先运行以下命令设置 API 密钥："
echo "   gemini config set api_key YOUR_API_KEY"
echo
