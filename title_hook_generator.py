#!/usr/bin/env python3
"""
标题钩子生成器
读取 items.json 中 hook_title 为空的条目，用 API 生成钩子标题
"""

import json
import os
import re
import time
from pathlib import Path

# API 配置
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "glm-5-turbo"

def load_env():
    """从 ~/.hermes/.env 加载环境变量"""
    global API_KEY
    env_file = Path("~/.hermes/.env").expanduser()
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # 只加载我们需要的变量
                if key == "ZHIPU_API_KEY" and not API_KEY:
                    API_KEY = value

def load_items():
    """加载 items.json"""
    items_file = Path("~/.hermes/data/browse/items.json").expanduser()
    try:
        with open(items_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_items(items):
    """保存 items.json"""
    items_file = Path("~/.hermes/data/browse/items.json").expanduser()
    with open(items_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def generate_hook_title(original_title, summary):
    """调用 API 生成钩子标题"""

    # 构建提示词
    prompt = f"""你是一个标题优化专家。把下面的原始标题和摘要改成一个有钩子（hook）的短标题，让人想点进去看。
要求：
- 不超过 30 个字
- 用具体数字、反常识、悬念或痛点来制造钩子
- 不要用"揭秘""震惊""你不知道"等标题党词
- 直接输出标题，不要引号或额外说明

原始标题：{original_title}
摘要：{summary[:200]}"""

    # 检查是否安装了 openai 包
    try:
        import openai
        use_openai_package = True
    except ImportError:
        use_openai_package = False

    try:
        if use_openai_package:
            # 使用 openai 包
            client = openai.OpenAI(
                api_key=API_KEY,
                base_url=BASE_URL
            )

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )

            result = response.choices[0].message.content.strip()
        else:
            # 使用 requests 直接调用
            import requests

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }

            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()["choices"][0]["message"]["content"].strip()

        # 清理结果
        result = result.strip('"\'')  # 去掉引号
        result = re.sub(r'^[：:]\s*', '', result)  # 去掉开头的冒号
        result = result[:30]  # 截断到30字

        # 避免频繁请求
        time.sleep(2)

        return result if result else ""

    except Exception as e:
        print(f"    ✗ API 调用失败: {e}")
        return ""

def process_batch(items, batch_size=10):
    """批量处理条目"""
    # 找出需要处理的条目
    pending = [item for item in items if not item.get("hook_title", "").strip()]

    if not pending:
        print("没有需要生成钩子标题的条目")
        return

    print(f"找到 {len(pending)} 条需要生成钩子标题的条目")

    # 只处理前 batch_size 条
    to_process = pending[:batch_size]
    print(f"本次处理前 {len(to_process)} 条")

    for i, item in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] 生成钩子标题: {item.get('original_title', '')[:30]}...")

        hook = generate_hook_title(
            item.get("original_title", ""),
            item.get("summary", "")
        )

        if hook:
            item["hook_title"] = hook
            print(f"  → {hook}")
        else:
            print(f"  ✗ 生成失败")

        # 避免频繁请求
        time.sleep(1)

        # 回写 items.json
        save_items(items)

    print(f"\n✅ 批次处理完成")

def main():
    """主函数"""
    # 加载环境变量
    load_env()

    if not API_KEY:
        print("❌ 未找到 API_KEY，请检查 OPENAI_API_KEY 或 ~/.hermes/.env 中的 ZHIPU_API_KEY")
        return

    print(f"使用模型: {MODEL}")
    print(f"API 地址: {BASE_URL}")

    # 加载条目
    items = load_items()
    if not items:
        print("❌ 未找到 items.json 或文件为空")
        return

    print(f"加载 {len(items)} 条条目")

    # 批量处理
    process_batch(items, batch_size=10)

if __name__ == "__main__":
    main()