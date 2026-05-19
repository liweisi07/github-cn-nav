# 参与贡献

想把好项目加进来？两种方式。

## 推荐项目

### 方式 1：提 Issue（最简单）

[新建 Issue](https://github.com/SoulSpark-CN/github-cn-nav/issues/new) → 选择"推荐项目"模板 → 填项目地址 + 一句话说明。

适合：纯推荐，不会改代码。

### 方式 2：提 PR

1. Fork 本仓库
2. 编辑 `manifest.json`，在末尾加一条（照着前面的格式）
3. 提 PR

适合：想亲手加上去，或者批量推荐。

## 修正翻译 / 分类

- **翻译不准**：直接改 `人话解读.json` 对应条目，提 PR
- **分类不对**：改 `phase3_enhanced.py` 的分类规则，说明为什么
- **漏了项目**：提 Issue 或按上面方式加

## 环境跑起来

```bash
git clone https://github.com/SoulSpark-CN/github-cn-nav.git
cd github-cn-nav
python3 -m http.server 8080 --directory deploy
# 浏览器打开 http://localhost:8080
```

## 数据规范

- 项目须 ≥ 5000 Star（GitHub 公开仓库）
- `manifest.json` 是单一真相来源，其他 JSON 由 `auto_update.py` 自动生成
- 人话解读格式见 `人话解读.json` 中任意一条
