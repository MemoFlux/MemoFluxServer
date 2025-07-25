#!/bin/bash

# MemoFluxServer 运行脚本
# 该脚本将在 macOS 上使用项目现有的虚拟环境运行 MemoFluxServer 项目

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 输出信息


echo "MemoFluxServer 启动脚本"
echo "========================"
echo "脚本目录: $SCRIPT_DIR"
echo "项目目录: $PROJECT_DIR"
echo

# 检查是否在 macOS 上运行
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误: 此脚本仅适用于 macOS 系统"
    exit 1
fi

# 检查 Python 3 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3，请先安装 Python 3"
    exit 1
fi

echo "系统 Python 3 版本: $(python3 --version)"
echo

# 设置现有虚拟环境路径
VENV_DIR="$PROJECT_DIR/.conda"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "错误: 未找到项目虚拟环境，请确保 .conda 目录存在且包含有效的 Python 环境"
    exit 1
fi

echo "使用项目虚拟环境: $VENV_DIR"
echo "虚拟环境 Python 版本: $($VENV_DIR/bin/python --version)"
echo

# 设置虚拟环境中的 Python 和 pip 路径
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# 升级 pip
echo "升级 pip..."
$VENV_PIP install --upgrade pip
echo

# 安装项目依赖
echo "安装/更新项目依赖..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    $VENV_PIP install -r "$PROJECT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "错误: 安装依赖失败"
        exit 1
    fi
    echo "依赖安装成功"
else
    echo "警告: 未找到 requirements.txt 文件"
fi

echo

# 检查 .env 文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "警告: 未找到 .env 文件，将使用默认配置"
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        echo "复制 .env.example 为 .env"
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    fi
fi

echo

# 运行应用
echo "启动 MemoFluxServer..."
echo "服务器将在 http://0.0.0.0:8000 上运行"
echo "按 Ctrl+C 停止服务器"
echo

cd "$PROJECT_DIR"
$VENV_PYTHON src/run.py

# 停止时的清理工作
if [ $? -eq 0 ]; then
    echo
    echo "服务器已正常停止"
else
    echo
    echo "服务器运行出错"
fi
