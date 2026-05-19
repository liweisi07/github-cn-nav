#!/bin/bash
# 一键更新: 搜索新项目 → 分类 → 翻译 → 人话 → 重建 → 部署
# 用法: ./update.sh [--dry-run]
cd "$(dirname "$0")"
python3 auto_update.py "$@"
