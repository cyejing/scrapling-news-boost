---
name: scrapling-web-fetch
description: web_fetch 的替代技能，支持反爬绕过和动态渲染。适合抓取博客、新闻、微信公众号文章等现代网页，输出结构化内容供大模型理解。
---

## 适用场景

**推荐使用：**
- 获取文章/博客/新闻正文
- 从网页提取标题和正文
- 常规 web_fetch 失败或效果差
- 需要绕过 Cloudflare 等反爬机制
- 页面存在动态渲染干扰

**不推荐使用：**
- 需要浏览器交互（点击、登录、翻页）→ 改用浏览器自动化
- 简单获取 API JSON → 直接请求 API

## 用法

```bash
# 基础用法（Markdown 输出）
uv run scripts/scrapling_fetch.py <url>

# 指定最大字符数
uv run scripts/scrapling_fetch.py <url> 10000

# JSON 结构化输出
uv run scripts/scrapling_fetch.py <url> 10000 --json

# 指定解析器
uv run scripts/scrapling_fetch.py <url> 10000 --parser <auto|trafilatura|scrapling>
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 目标 URL | 必填 |
| `max_chars` | 最大输出字符数 | 10000 |
| `--json` | JSON 格式输出 | false |
| `--parser` | 解析器：auto（自动降级）、trafilatura、scrapling | auto |

## 输出示例

**Markdown 模式：**
```markdown
# 文章标题

> URL: https://example.com
> 内容长度: 5000 字符 
> 抓取模式: stealth | 解析器: trafilatura
> 耗时: 抓取 4.89s + 解析 0.67s = 总计 5.56s

---

正文内容...
```

**JSON 模式：**
```json
{
  "ok": true,
  "url": "https://example.com",
  "title": "文章标题",
  "content_length": 5000,
  "fetch_mode": "stealth",
  "parser": "trafilatura",
  "fetch_duration": 4.89,
  "parse_duration": 0.67,
  "total_duration": 5.56,
  "content": "正文内容..."
}
```

## 技术架构

**三级抓取策略：**
1. `StealthyFetcher` - 模拟真实浏览器，最佳反爬绕过
2. `Fetcher` - 基础抓取，带隐蔽请求头
3. `urllib` - 纯 Python 回退方案

**两级解析策略：**
1. `Trafilatura`（主要）- 智能正文识别，噪音清理更好
2. `Scrapling`（降级）- 原生文本提取，Trafilatura 失败时自动降级

## 依赖安装

```bash
uv sync                                    # 安装项目依赖
playwright install chromium                # 安装 Chromium 浏览器
```

## 自我提升

使用该技能后，如果返回内容存在问题：
1. 抓取失败，有报错输出
2. 正文内容比较少，有一些疑似被拦截或者抓取错误的内容
4. 正文内容噪音过多
3. 抓取时间超时（>30秒）


当发生上述问题时，在 `logs.jsonl` 文件追加记录：
```json
{"timestamp":"2026-03-16T14:30:25+08:00","url":"https://example.com","status":"成功","fetch_mode":"stealth","parser":"trafilatura","text_length":5234,"quality_score":85,"comment":"少量噪音"}
```

| 字段 | 说明 |
|------|------|
| timestamp | ISO 时间 |
| url | 原始 URL |
| status | 成功/失败 |
| fetch_mode | stealth/fetcher/urllib |
| parser | trafilatura/scrapling |
| text_length | 文本字符数 |
| quality_score | 质量评分 0-100 |
| comment | 问题描述 |

**质量评分标准（0-100分）：**

90-100：内容完整，噪音清除干净
70-89：内容基本完整，有少量噪音
50-69：内容有缺失或噪音较多
0-49：抓取失败或内容严重缺失
