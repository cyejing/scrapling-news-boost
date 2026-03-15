# 改进 site_test.py 脚本计划

## 目标

将 `site_test.py fetch` 命令改为支持直接输出到 JSONL 文件，类似于 `fetch_all_results.jsonl` 的生成方式。

## 当前问题

1. `fetch` 命令将 JSON 结果输出到 stdout，需要手动重定向
2. 进度信息输出到 stderr，需要 `2>/dev/null` 过滤
3. 没有内置的输出文件参数

## 改进方案

### 1. 添加 `--output` 参数

为 `fetch` 子命令添加 `--output` 参数：
- 支持指定输出文件路径
- 输出格式为 JSONL（每行一个 JSON 对象）
- 不指定时保持原有行为（输出到 stdout）

### 2. 修改 `cmd_fetch` 函数

```python
def cmd_fetch(args):
    data = load_cases()
    cases = data["cases"]
    
    # 过滤逻辑保持不变
    if args.id:
        ids = [x.strip() for x in args.id.split(",")]
        cases = [c for c in cases if c["id"] in ids]
    elif not args.all:
        cases = [c for c in cases if c["status"] != "passed"]
    
    if not cases:
        print(json.dumps({"error": "No cases to test"}))
        return
    
    # 打开输出文件（如果指定）
    output_file = None
    if args.output:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = open(args.output, "w", encoding="utf-8")
    
    try:
        for case in cases:
            print(f"--- Testing {case['id']}: {case['domain']} ---", file=sys.stderr)
            fetch_result = fetch_case(case)
            
            output = {
                "id": case["id"],
                "domain": case["domain"],
                "url": case["url"],
                "fetch_result": fetch_result,
            }
            line = json.dumps(output, ensure_ascii=False)
            
            if output_file:
                output_file.write(line + "\n")
            else:
                print(line)
    finally:
        if output_file:
            output_file.close()
            print(f"Results saved to: {args.output}", file=sys.stderr)
```

### 3. 更新参数解析器

```python
fetch_parser.add_argument("--output", "-o", help="Output file path (JSONL format)")
```

## 默认输出文件

当使用 `--output` 但不指定路径时，默认输出到 `output/test_fetch_all_results.jsonl`。

## 使用示例

```bash
# 输出到默认文件 output/test_fetch_all_results.jsonl
uv run scripts/site_test.py fetch --all --output

# 输出到指定文件
uv run scripts/site_test.py fetch --all --output output/custom_results.jsonl

# 输出到 stdout（原有行为）
uv run scripts/site_test.py fetch --all

# 测试指定用例并输出到文件
uv run scripts/site_test.py fetch --id 02,05,08 --output output/partial_results.jsonl
```

## 实现步骤

1. 修改 `cmd_fetch` 函数，添加文件输出支持
2. 在 `fetch_parser` 中添加 `--output` 参数
3. 测试验证
