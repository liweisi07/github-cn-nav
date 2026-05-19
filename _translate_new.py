#!/usr/bin/env python3
"""
Auto-translate new & previously untranslated repos using rule engine.
Appends to existing done files.
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(BASE, "manifest.json")

def is_cn(s):
    return sum(1 for c in s if '\u4e00' <= c <= '\u9fff') > len(s) * 0.25

def strip_emoji(s):
    return re.sub(r'^[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF\uFE00-\uFE0F\u200D]+', '', s).strip()

def translate_v2(desc):
    """Rule-based EN→CN translation"""
    d = desc.strip()
    if not d:
        return d
    if is_cn(d):
        return d
    
    # Extract actual description text (remove emoji/icon prefixes at start)
    d_clean = d
    # Remove leading symbols like ●, ◆, 🎨, ⚡ etc
    d_clean = re.sub(r'^[●◆◆▪️▶️🔹🔸🔺🟢🔴🟣🟡🔵⚪🟤🟠🔘📦🚀🔥⭐💡🎯🔧🛠⚙🔗🔑🛡💻📱🌐🔄📊🎨⚡🦀🐍🦕]+', '', d_clean).strip()
    # Remove leading markdown/label prefixes like "### " or "**" 
    d_clean = re.sub(r'^[\*#\-\s]+', '', d_clean).strip()
    d_clean = strip_emoji(d_clean)
    
    if not d_clean or len(d_clean) < 5:
        return f"[EN]{d}"
    
    orig = d_clean
    
    # Pattern: "A/B/C | X" - split and translate each part
    if " | " in d_clean:
        parts = d_clean.split(" | ")
        translated_parts = []
        for p in parts:
            t = translate_v2(p.strip())
            if t and t != p.strip():
                translated_parts.append(t)
            else:
                translated_parts.append(p.strip())
        return " | ".join(translated_parts)
    
    # "Official X of Y" pattern
    m = re.match(r'^(The|An?)\s+(official|open-source|open source|free|modern|lightweight|powerful|simple|minimal|fast|high-performance|cross-platform|next-generation|next-gen|full-featured|production-ready|battle-tested|scalable|flexible|easy-to-use|easy to use)\s+(.+)$', d_clean, re.I)
    if m:
        adj = m.group(2).lower()
        adj_map = {
            "official": "官方", "open-source": "开源", "open source": "开源",
            "free": "免费", "modern": "现代", "lightweight": "轻量",
            "powerful": "强大", "simple": "简洁", "minimal": "极简",
            "fast": "高速", "high-performance": "高性能",
            "cross-platform": "跨平台", "next-generation": "下一代",
            "next-gen": "下一代", "full-featured": "全功能",
            "production-ready": "生产就绪", "battle-tested": "久经考验",
            "scalable": "可扩展", "flexible": "灵活",
            "easy-to-use": "易用", "easy to use": "易用",
        }
        cn_adj = adj_map.get(adj, adj)
        rest = m.group(3)
        return f"{cn_adj}{rest}"
    
    # "A for B" simple
    m = re.match(r'^(.+?)\s+(?:for|of|in|on)\s+(.+?)$', d_clean)
    if m and len(d_clean.split()) <= 10:
        x = m.group(1).strip()
        y = m.group(2).strip()
        # Remove trailing punctuation from x
        x = x.rstrip('.,;:!?')
        # Check if y has more structure
        if re.match(r'^(the|your|a|an)\s+', y, re.I):
            return f"用于{y}的{x}"
        return f"用于{y}的{x}"
    
    # "X is Y"
    m = re.match(r'^(.+?)\s+is\s+(an?\s+)?(.+)$', d_clean)
    if m:
        name_part = m.group(1).strip()
        rest = m.group(3).strip()
        return f"{name_part}：{rest}"
    
    # "X - Y" pattern (dash separator)
    if " — " in d_clean or " – " in d_clean or " - " in d_clean:
        sep = " — " if " — " in d_clean else (" – " if " – " in d_clean else " - ")
        parts = d_clean.split(sep, 1)
        if len(parts) == 2 and len(parts[1]) > 5:
            return parts[1]
    
    # "Build/Create/Develop X" pattern
    m = re.match(r'^(Build|Create|Develop|Make|Design|Write|Run|Deploy|Manage|Monitor|Visualize|Generate|Automate)\s+(.+)$', d_clean, re.I)
    if m:
        action = m.group(1).lower()
        action_map = {
            "build": "构建", "create": "创建", "develop": "开发",
            "make": "制作", "design": "设计", "write": "编写",
            "run": "运行", "deploy": "部署", "manage": "管理",
            "monitor": "监控", "visualize": "可视化",
            "generate": "生成", "automate": "自动化",
        }
        cn_act = action_map.get(action, action)
        rest = m.group(2)
        return f"{cn_act}{rest}"
    
    # "X built with Y" / "X based on Y"
    m = re.match(r'^(.+?)\s+(built|based)\s+(?:with|on|upon)\s+(.+)$', d_clean, re.I)
    if m:
        x = m.group(1).strip()
        y = m.group(3).strip()
        return f"基于{y}的{x}"
    
    # Static analysis, tool, framework, library patterns
    for prefix, cn_prefix in [
        ("static analysis", "静态分析"),
        ("dynamic analysis", "动态分析"),
        ("real-time", "实时"),
        ("command-line", "命令行"),
        ("cli", "命令行"),
    ]:
        if d_clean.lower().startswith(prefix):
            rest = d_clean[len(prefix):].strip().lstrip(',;:').strip()
            if rest:
                return f"{cn_prefix}{rest}"
            return cn_prefix
    
    # Fallback: if short, add [EN] marker
    if len(d_clean.split()) <= 6:
        return f"[EN]{d_clean}"
    
    return f"[EN]{d_clean}"


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        repos = json.load(f)
    
    # Load existing done sets
    done_sets = {}  # batch_file -> dict of name->item
    for bf in ['translate_batch_0_done.json', 'translate_batch_1_done.json',
               'translate_batch_2_done.json', 'translate_batch_3_done.json']:
        fp = os.path.join(BASE, bf)
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
            done_sets[bf] = {item['name']: item for item in data}
        else:
            done_sets[bf] = {}
    
    # Find ALL untranslated repos (not in any done file)
    all_done_names = set()
    for items in done_sets.values():
        all_done_names.update(items.keys())
    
    untranslated = []
    for i, r in enumerate(repos):
        if r['name'] not in all_done_names:
            untranslated.append((i, r))
    
    print(f"待翻译总数: {len(untranslated)}")
    
    translated = 0
    for idx, r in enumerate(untranslated[:200]):  # Process in batches
        real_idx = r[0]
        repo_data = r[1]
        desc = repo_data.get("desc", "") or ""
        
        # Translate
        zh = translate_v2(desc)
        
        # Determine which batch file this belongs to based on index
        if real_idx < 1578:
            batch_file = 'translate_batch_0_done.json'
        elif real_idx < 3156:
            batch_file = 'translate_batch_1_done.json'
        elif real_idx < 4734:
            batch_file = 'translate_batch_2_done.json'
        else:
            batch_file = 'translate_batch_3_done.json'
        
        entry = {
            'idx': real_idx,
            'name': repo_data['name'],
            'desc_zh': zh
        }
        
        done_sets[batch_file][repo_data['name']] = entry
        
        status = "✓" if zh and not zh.startswith("[EN]") else "○"
        desc_short = desc[:50].replace("\n", " ")
        zh_short = zh[:40] if zh else "(空)"
        print(f"  {status} [{real_idx}] {repo_data['name']:45s} {zh_short}")
        translated += 1
    
    # Save all batch files
    total_saved = 0
    for bf, items in done_sets.items():
        fp = os.path.join(BASE, bf)
        # Convert to list and sort by idx
        data_list = list(items.values())
        data_list.sort(key=lambda x: x['idx'])
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
        total_saved += len(data_list)
        print(f"  💾 {bf}: {len(data_list)} 条")
    
    print(f"\n✅ 翻译完成: {translated} 条, 总翻译: {total_saved} 条")


if __name__ == "__main__":
    main()
