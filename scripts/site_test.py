#!/usr/bin/env python3
"""
Site test script for scrapling-web-fetch skill.

Commands:
  --fetch              Fetch test cases and output results
  --save-result        Save test result to output/
  --update-case        Update case status in cases.json

Usage:
  uv run site_test.py --fetch [--id 02,05,08] [--all]
  uv run site_test.py --save-result --id 02 --status failed --score 10 --comment "..." --content "..."
  uv run site_test.py --update-case --id 02 --status failed --score 10 --comment "..."
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CASES_FILE = Path(__file__).parent.parent / "cases.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
FETCH_RESULT_FILE = OUTPUT_DIR / "fetch_result.json"

STATUS_DISPLAY = {
    "passed": "✅ 通过",
    "failed": "❌ 失败",
    "timeout": "⚠️ 超时",
    "pending": "",
}


def load_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cases(data):
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_case(case):
    url = case["url"]
    script_dir = Path(__file__).parent
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    FETCH_RESULT_FILE.write_text("{}", encoding="utf-8")
    
    cmd = [
        "uv", "run", str(script_dir / "scrapling_fetch.py"),
        url, "15000", "--json",
        "--output", str(FETCH_RESULT_FILE)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            return {"ok": False, "error": result.stderr or "Unknown error"}
        
        with open(FETCH_RESULT_FILE, "r", encoding="utf-8") as f:
            fetch_result = json.load(f)
        
        if not fetch_result:
            return {"ok": False, "error": "Empty result file"}
        
        return {"ok": True, **fetch_result}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout after 180s"}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"JSON decode error: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def cmd_fetch(args):
    data = load_cases()
    cases = data["cases"]
    
    if args.id:
        ids = [x.strip() for x in args.id.split(",")]
        cases = [c for c in cases if c["id"] in ids]
    elif not args.all:
        cases = [c for c in cases if c["status"] != "passed"]
    
    if not cases:
        print(json.dumps({"error": "No cases to test"}))
        return
    
    for case in cases:
        print(f"--- Testing {case['id']}: {case['domain']} ---", file=sys.stderr)
        fetch_result = fetch_case(case)
        
        output = {
            "id": case["id"],
            "domain": case["domain"],
            "url": case["url"],
            "fetch_result": fetch_result,
        }
        print(json.dumps(output, ensure_ascii=False))


def cmd_save_result(args):
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    data = load_cases()
    case = next((c for c in data["cases"] if c["id"] == args.id), None)
    if not case:
        print(f"Error: Case {args.id} not found")
        sys.exit(1)
    
    status_display = STATUS_DISPLAY.get(args.status, args.status)
    
    content = f"""## 测试结果
- **编号**：{args.id}
- **原始 URL**：{case['url']}
- **抓取状态**：{status_display}
- **抓取模式**：{args.fetch_mode or '-'}
- **解析器**：{args.parser or '-'}
- **文本长度**：{args.content_length or '-'}

## 质量评分：{args.score} 分

## 问题分析
{args.comment}

## 优化建议

"""
    
    filename = f"{args.id}_{case['domain']}.md"
    output_path = OUTPUT_DIR / filename
    output_path.write_text(content, encoding="utf-8")
    print(f"Saved: {output_path}")


def cmd_update_case(args):
    data = load_cases()
    
    for case in data["cases"]:
        if case["id"] == args.id:
            case["status"] = args.status
            case["quality_score"] = args.score
            case["quality_comment"] = args.comment
            break
    else:
        print(f"Error: Case {args.id} not found")
        sys.exit(1)
    
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_cases(data)
    print(f"Updated case {args.id}: status={args.status}, score={args.score}")


def main():
    parser = argparse.ArgumentParser(description="Site test script")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    fetch_parser = subparsers.add_parser("fetch", help="Fetch test cases")
    fetch_parser.add_argument("--id", help="Comma-separated case IDs to test")
    fetch_parser.add_argument("--all", action="store_true", help="Test all cases including passed")
    
    save_parser = subparsers.add_parser("save-result", help="Save test result")
    save_parser.add_argument("--id", required=True, help="Case ID")
    save_parser.add_argument("--status", required=True, choices=["passed", "failed", "timeout", "pending"])
    save_parser.add_argument("--score", required=True, type=int)
    save_parser.add_argument("--comment", required=True)
    save_parser.add_argument("--fetch-mode", dest="fetch_mode")
    save_parser.add_argument("--parser")
    save_parser.add_argument("--content-length", dest="content_length", type=int)
    
    update_parser = subparsers.add_parser("update-case", help="Update case status")
    update_parser.add_argument("--id", required=True, help="Case ID")
    update_parser.add_argument("--status", required=True, choices=["passed", "failed", "timeout", "pending"])
    update_parser.add_argument("--score", required=True, type=int)
    update_parser.add_argument("--comment", required=True)
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "save-result":
        cmd_save_result(args)
    elif args.command == "update-case":
        cmd_update_case(args)


if __name__ == "__main__":
    main()
