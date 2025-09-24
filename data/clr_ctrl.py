import json
import re
import os

# 定义用于去除控制字符和非法json字符的正则表达式
control_chars = re.compile(r'[\x00-\x1F\x7F]')

# 保留中文、英文、数字和常见标点的正则
allowed_chars = re.compile(r'[^\u4e00-\u9fffA-Za-z0-9，。！？、；：“”‘’（）《》〈〉—…·.,!?;:"\'()\[\]{}<>/\-_=+@#$%^&*]')

def filter_text(text):
    """过滤非法字符，只保留中文、英文、数字和常见标点"""
    return allowed_chars.sub('', text)

def clean_json_line(line):
    """清理 JSON 行，去除控制字符和非法转义"""
    line = control_chars.sub('', line)  # 去除控制字符
    line = line.strip()
    line = re.sub(r'\\(?!["\\/bfnrtu])', '', line)  # 去除孤立的反斜杠
    line = re.sub(r'[\u202a-\u202e\u200b-\u200f]', '', line)  # 去除不可见字符
    return line

def process_wiki_folder(wiki_root, output_path):
    all_texts = []
    for root, dirs, files in os.walk(wiki_root):
        for file in files:
            if not file.startswith("wiki_"):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = clean_json_line(line)
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            text = obj.get("text", "")
                            if text:
                                text = filter_text(text.replace("\\n", "\n"))
                                if text.strip():
                                    all_texts.append(text)
                        except Exception:
                            continue
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")

    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(all_texts, fout, ensure_ascii=False)

    print(f"已保存清理后的 Wiki 语料到 {output_path}（单行 JSON 数组）")

def process_json_file(input_path, output_path):
    all_texts = []
    with open(input_path, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = clean_json_line(line)
            if not line:
                continue
            try:
                obj = json.loads(line)
                text = obj.get("text", "")
                if text:
                    text = filter_text(text.replace("\\n", "\n"))
                    if text.strip():
                        all_texts.append(text)
            except Exception:
                continue

    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(all_texts, fout, ensure_ascii=False)

    print(f"已保存清理后的 JSON 文件到 {output_path}（单行 JSON 数组）")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="清理控制字符，仅保留中文、英文和常见标点，合并成一个单行 JSON 数组")
    parser.add_argument('--input_json', type=str, default='input.json', help='输入的 JSON 文件路径')
    parser.add_argument('--wiki_dir', type=str, default='wiki_zh', help='Wiki 语料目录')
    parser.add_argument('--output_json', type=str, default='train.json', help='输出的 JSON 文件路径')
    parser.add_argument('--output_wiki', type=str, default='train_wiki.json', help='输出的 Wiki JSON 文件路径')
    parser.add_argument('--mode', type=str, choices=['json', 'wiki'], required=True, help='处理模式: json 或 wiki')
    args = parser.parse_args()

    if args.mode == 'json':
        process_json_file(args.input_json, args.output_json)
    elif args.mode == 'wiki':
        process_wiki_folder(args.wiki_dir, args.output_wiki)
# 用法示例：
# python clr_ctrl.py --mode json --input_json input.json --output_json train.json
# python clr_ctrl.py --mode wiki --wiki_dir wiki_zh --output_wiki train_wiki.json