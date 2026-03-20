---
name: scrapling-web-fetch
description: 当 web_fetch 抓取失败时的替代方案，专为现代网站设计。自动绕过 Cloudflare 等反爬机制，支持 JavaScript 动态渲染，精准提取文章正文。输出干净、结构化的 Markdown 或 JSON 格式，为大模型提供高质量输入。
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

使用该技能后，如果返回内容存在问题，应在 `site_config.json` 中添加或修改对应网站的配置：

**触发条件：**
1. 网站有 Cloudflare 保护导致抓取失败
2. 正文内容比较少，疑似被拦截或抓取错误
3. 正文内容噪音过多
4. 抓取时间超时（>30秒）

**配置示例：**
```json
[
  {
    "domain": "example.com",
    "wait_for": "article",
    "content_selector": "#content",
    "network_idle": true,
    "solve_cloudflare": true,
    "original_url": "https://example.com/article/123",
    "comment": "正文内容缺失，需要等待 article 元素加载"
  }
]
```

**配置字段说明：**

| 字段            | 说明                               |
|-----------------|------------------------------------|
| domain          | 网站域名，支持通配符如 `*.example.com` |
| wait_for        | 等待指定元素出现后再抓取             |
| content_selector | CSS 选择器，提取指定区域内容         |
| network_idle    | 等待网络空闲后再抓取                 |
| solve_cloudflare | 是否启用 Cloudflare 绕过            |
| original_url     | 记录触发配置的原始 URL              |
| comment          | 配置说明，记录问题原因              |

**操作步骤：**
1. 如果网站有 Cloudflare 导致抓取失败，在 `site_config.json` 中添加配置，设置 `solve_cloudflare: true`
2. 如果抓取内容存在问题，尝试修改 `wait_for`、`content_selector`、`network_idle` 等配置项
3. 每次修改配置时，在配置中添加 `original_url` 和 `comment` 字段记录问题

