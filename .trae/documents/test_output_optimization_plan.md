# 测试流程优化计划

## 目标

修改测试流程，让 `scrapling_fetch.py` 将结果输出到文件，而不是 stdout，避免大量内容通过管道传递。

## 当前流程

```
site_test.py fetch
    ↓
subprocess.run(scrapling_fetch.py --json)
    ↓
从 stdout 读取 JSON 结果
    ↓
返回给大模型评估
```

## 新流程

```
site_test.py fetch
    ↓
清空 output/fetch_result.json
    ↓
subprocess.run(scrapling_fetch.py --json --output output/fetch_result.json)
    ↓
读取 output/fetch_result.json
    ↓
返回给大模型评估
```

## 实现步骤

### 步骤 1：修改 scrapling_fetch.py

添加 `--output` 参数，支持将 JSON 结果输出到指定文件：

```python
arg_parser.add_argument(
    "--output",
    help="Output file path for JSON result (only works with --json)",
)
```

当指定 `--output` 时，将 JSON 写入文件而不是 stdout。

### 步骤 2：修改 site_test.py

修改 `fetch_case` 函数：

1. 每次测试前清空 `output/fetch_result.json`
2. 调用 `scrapling_fetch.py` 时添加 `--output output/fetch_result.json` 参数
3. 从文件读取结果而不是从 stdout

```python
FETCH_RESULT_FILE = OUTPUT_DIR / "fetch_result.json"

def fetch_case(case):
    # 清空结果文件
    FETCH_RESULT_FILE.write_text("{}")
    
    cmd = ["uv", "run", str(script_dir / "scrapling_fetch.py"), url, "15000", "--json", "--output", str(FETCH_RESULT_FILE)]
    
    subprocess.run(cmd, timeout=180)
    
    # 从文件读取结果
    with open(FETCH_RESULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
```

## 文件清单

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| 修改 | `scripts/scrapling_fetch.py` | 添加 --output 参数 |
| 修改 | `scripts/site_test.py` | 修改 fetch_case 函数 |
