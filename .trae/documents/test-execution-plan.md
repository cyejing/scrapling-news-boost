# 测试执行问题分析与改进计划

## 一、执行问题分析

上次测试执行存在以下问题：

### 1. 未保存测试结果到 output/ 目录
- 测试结果只输出到终端，没有保存到 `output/{编号}_{域名}.md` 文件

### 2. 测试报告缺少质量评分
- 虽然 `site-test.md` 中定义了质量评分标准，但测试输出中没有包含评分

### 3. 未更新测试网站列表表格
- 测试完成后没有更新 `site-test.md` 中的状态、质量评分、质量评价字段

---

## 二、失败网站原因分析

### 02 - finance.sina.com.cn（噪音过多）

**问题现象**：抓取内容全是侧边栏、推荐文章、广告等噪音，正文内容缺失

**原因分析**：
- 新浪财经页面结构复杂，正文区域可能使用了特殊的 HTML 结构
- Trafilatura 无法正确识别正文区域，误抓了页面其他内容

### 05 - www.msn.cn（Cookie政策 + 超时）

**问题现象**：
- 抓取内容全是 Cookie 政策文本
- 抓取耗时 131.8 秒

**原因分析**：
- MSN 网站有 Cookie 同意弹窗，StealthyFetcher 可能没有正确处理
- 页面可能需要等待 Cookie 弹窗关闭后才能获取正文

### 08 - sports.huanqiu.com（AdBlock提示）

**问题现象**：抓取内容是 AdBlock 检测提示，正文缺失

**原因分析**：
- 环球网检测到模拟浏览器行为，触发了反爬机制
- 页面检测到 AdBlock 后隐藏了正文内容

### 09/11 - guancha.cn / sina.cn（超时但内容正常）

**问题现象**：抓取成功但耗时超过 2 分钟

**原因分析**：
- StealthyFetcher 默认等待时间过长
- 页面可能有大量动态加载内容

---

## 三、代码架构设计

### 设计原则
- 针对特殊网站的优化**不**写在现有逻辑代码里
- 每个域名的优化独立配置，放到 `scripts/spec/` 目录
- 用域名作为文件名，如 `finance.sina.com.cn.py`
- 主脚本自动加载匹配的配置

### 目录结构

```
scripts/
├── scrapling_fetch.py          # 主入口脚本
├── fetcher/
│   └── scrapling_fetcher.py    # 抓取模块
├── parsers/
│   └── ...                     # 解析模块
├── format/
│   └── formatters.py           # 格式化模块
└── spec/                       # 域名特定配置目录（新增）
    ├── __init__.py             # 配置加载器
    ├── base.py                 # 配置基类
    ├── finance.sina.com.cn.py  # 新浪财经配置
    ├── www.msn.cn.py           # MSN 配置
    ├── sports.huanqiu.com.py   # 环球体育配置
    └── ...                     # 其他域名配置
```

### 配置基类设计

```python
# scripts/spec/base.py
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class SiteSpec:
    domains: list[str] = field(default_factory=list)
    
    fetch_timeout: int | None = None
    fetch_wait_selector: str | None = None
    fetch_extra_headers: dict | None = None
    
    parser_preference: str = "auto"
    parser_exclude_selectors: list[str] = field(default_factory=list)
    
    post_process: Callable[[str], str] | None = None
```

### 配置示例

```python
# scripts/spec/finance.sina.com.cn.py
from spec.base import SiteSpec

class FinanceSinaSpec(SiteSpec):
    domains = ["finance.sina.com.cn", "news.sina.com.cn"]
    
    parser_exclude_selectors = [
        ".sidebar", ".recommend", ".hot-news", 
        ".stock-list", ".live-room"
    ]
    
    def post_process(content: str) -> str:
        # 清理噪音内容
        ...
```

### 主脚本集成

修改 `scrapling_fetch.py`：
1. 解析 URL 获取域名
2. 从 `spec/` 目录加载匹配的配置
3. 应用配置到抓取和解析流程

---

## 四、实施步骤

### 步骤 1：创建 spec 目录和基础架构
- 创建 `scripts/spec/` 目录
- 创建 `base.py` 配置基类
- 创建 `__init__.py` 配置加载器

### 步骤 2：修改主脚本支持配置加载
- 修改 `scrapling_fetch.py` 加载域名配置
- 修改 `scrapling_fetcher.py` 支持配置参数
- 修改解析器支持排除选择器

### 步骤 3：创建失败网站的配置文件
- 创建 `finance.sina.com.cn.py`
- 创建 `www.msn.cn.py`
- 创建 `sports.huanqiu.com.py`

### 步骤 4：创建 output 目录
- 创建 `output/` 目录用于保存测试结果

### 步骤 5：重新执行测试
- 执行前 10 个测试
- 保存结果到 `output/{编号}_{域名}.md`
- 人工评估质量评分

### 步骤 6：更新测试网站列表
- 更新 `site-test.md` 中的状态、质量评分、质量评价

### 步骤 7：记录问题到 logs.md
- 对失败的网站记录详细问题

---

## 五、测试结果文件格式

每个测试结果文件 `output/{编号}_{域名}.md`：

```markdown
# 测试结果

| 字段 | 值 |
|------|-----|
| 编号 | 01 |
| 原始 URL | https://... |
| 抓取状态 | 成功/失败 |
| 抓取模式 | stealth |
| 解析器 | trafilatura |
| 文本长度 | 5000 |
| 质量评分 | 85 |

## 抓取内容

[完整内容]
```
