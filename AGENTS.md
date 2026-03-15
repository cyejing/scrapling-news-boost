# Scrapling News Boost 项目规则

## 项目概述

本项目是一个通用技能（Skill），用于使用 Scrapling 抓取网页，Trafilatura 解析正文内容，输出结构化内容供大模型理解。核心目标是清除噪音，只保留主要内容信息，减少大模型的 token 消耗。

## 项目结构

```
scrapling-news-boost/
├── SKILL.md              # 技能入口描述文件，供大模型理解技能用途和使用方法
├── output/               # 测试输出目录
├── cases.json            # 测试用例配置文件
├── scripts/
│   ├── scrapling_fetch.py # 主入口脚本
│   ├── site_test.py       # 测试脚本
│   ├── fetcher/           # 抓取模块
│   │   └── scrapling_fetcher.py
│   ├── parsers/           # 解析模块
│   │   ├── base.py        # 解析器基类
│   │   ├── trafilatura_parser.py
│   │   ├── scrapling_parser.py
│   │   └── manager.py
│   └── format/            # 格式化模块
│       └── formatters.py
├── references/
│   └── usage.md          # 用法参考文档
├── site-test.md          # 测试网站列表（仅在明确要求全局测试时执行）
└── AGENTS.md             # 本文件：项目规则文档
```

## 核心脚本说明

### scrapling_fetch.py

主要逻辑流程：
1. **网页抓取**：使用 Scrapling 的三级回退机制
   - `StealthyFetcher`（stealth 模式）：最佳反爬绕过能力
   - `Fetcher`（fetcher 模式）：基础抓取，带隐蔽请求头
   - `urllib`（urllib 模式）：纯 Python 回退方案

2. **内容解析**：支持两种解析器
   - `Trafilatura`：智能正文识别，噪音清理更好（默认）
   - `Scrapling`：原生 `get_all_text()` 方法（降级方案）

3. **输出格式**：JSON 或 Markdown


## 测试规则

### 测试文件

`site-test.md` 包含测试用例网站列表和测试要求。

### 测试触发条件

- **仅在用户明确要求"全局测试"时执行** site-test.md 中的所有测试网站
- 单个网站测试可随时执行

## 代码修改规范

- 使用 Python 3.10+ 语法
- 不添加注释
- 代码简洁优雅
- 错误日志输出到标准输出
- markdown 表格内容要对齐，保持一致的列宽