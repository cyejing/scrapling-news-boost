# 将 print 替换为 Python logging 日志系统

## 概述

将项目中所有使用 `print()` 输出日志信息的代码替换为 Python 标准库 `logging` 模块，实现分级日志输出。

## 当前 print 语句分析

共发现 **14 处** print 语句，分布如下：

| 文件 | 行号 | 当前级别 | 说明 |
|------|------|----------|------|
| `scrapling_fetch.py` | 53 | ERROR | 抓取失败日志 |
| `scrapling_fetch.py` | 56 | INFO | 抓取成功日志 |
| `scrapling_fetch.py` | 65 | ERROR | 解析失败日志 |
| `scrapling_fetch.py` | 68 | INFO | 解析成功日志 |
| `scrapling_fetch.py` | 89-91 | 输出 | **最终结果输出，保留 print** |
| `scrapling_fetcher.py` | 108 | WARN | scrapling 未安装警告 |
| `scrapling_fetcher.py` | 110 | WARN | StealthyFetcher 失败警告 |
| `scrapling_fetcher.py` | 117 | WARN | Fetcher 失败警告 |
| `scrapling_fetcher.py` | 122 | ERROR | 所有抓取方法失败 |
| `manager.py` | 24 | INFO | Trafilatura 回退信息 |
| `manager.py` | 33 | WARN | 未知解析器警告 |
| `scrapling_parser.py` | 61 | WARN | Scrapling 解析错误 |
| `trafilatura_parser.py` | 67 | WARN | Trafilatura 解析错误 |

## 实施步骤

### 步骤 1：创建日志配置模块

创建 `scripts/logger.py`，配置统一的日志格式：

```python
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

### 步骤 2：修改 scrapling_fetch.py

- 导入 logger 模块
- 替换 4 处日志 print 为对应级别 logging 调用
- **保留** 第 89-91 行的最终结果输出（使用 print）

### 步骤 3：修改 fetcher/scrapling_fetcher.py

- 导入 logger 模块
- 替换 4 处日志 print 为对应级别 logging 调用

### 步骤 4：修改 parsers/manager.py

- 导入 logger 模块
- 替换 2 处日志 print 为对应级别 logging 调用

### 步骤 5：修改 parsers/scrapling_parser.py

- 导入 logger 模块
- 替换 1 处日志 print 为对应级别 logging 调用

### 步骤 6：修改 parsers/trafilatura_parser.py

- 导入 logger 模块
- 替换 1 处日志 print 为对应级别 logging 调用

## 日志级别映射

| 原 print 前缀 | logging 级别 |
|---------------|--------------|
| `ERROR:` | `logger.error()` |
| `WARN:` | `logger.warning()` |
| `INFO:` | `logger.info()` |

## 日志格式

输出格式：`{LEVEL}: {message}`

示例：
```
INFO: [Fetch] success with mode=stealth, html_length=12345, took=2.35s
WARNING: StealthyFetcher failed (timeout), trying Fetcher
ERROR: [Fetch] all fetch methods failed: timeout
```

## 文件修改清单

1. **新建** `scripts/logger.py` - 日志配置模块
2. **修改** `scripts/scrapling_fetch.py` - 替换 4 处日志
3. **修改** `scripts/fetcher/scrapling_fetcher.py` - 替换 4 处日志
4. **修改** `scripts/parsers/manager.py` - 替换 2 处日志
5. **修改** `scripts/parsers/scrapling_parser.py` - 替换 1 处日志
6. **修改** `scripts/parsers/trafilatura_parser.py` - 替换 1 处日志
