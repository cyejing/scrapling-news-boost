# Cookie 弹窗点击方案分析

## 问题背景

编号05（MSN）网站有 Cookie 隐私弹窗，需要点击"我同意"按钮才能获取正文内容。当前 `StealthyFetcher.fetch()` 无法进行点击交互。

## 方案分析

### 方案：在 SiteConfig 中支持配置 page.click 点击 Cookie 弹窗

#### 可行性评估：❌ 不可行（直接实现）

**原因分析**：

1. **Scrapling API 限制**

   * `StealthyFetcher.fetch()` 是**一次性请求**方法，返回 `Selector` 对象

   * 返回的 `Selector` 对象**不是** Playwright 的 `Page` 对象

   * 无法在 fetch 之后进行点击操作

2. **当前代码结构**

   ```python
   # 当前实现
   page = StealthyFetcher.fetch(url, ...)  # 返回 Selector，不是 Playwright Page
   html_content = page.html_content  # 只能读取，无法交互
   ```

3. **Scrapling 的交互能力**

   * `StealthyFetcher` - 一次性请求，无交互能力

   * `StealthySession` - 支持 session 管理，但需要重构

   * `DynamicSession` - 完整浏览器自动化，支持点击

#### 替代方案

**方案A：使用 StealthySession（推荐）**

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True) as session:
    page = session.fetch(url, network_idle=True)
    # 点击 Cookie 弹窗
    accept_btn = page.css('button#onetrust-accept-btn-handler')
    if accept_btn:
        # 需要访问底层 Playwright page 进行点击
        session.page.click('button#onetrust-accept-btn-handler')
    page = session.fetch(url, network_idle=True)  # 重新获取
```

**改动评估**：

* 需要重构 `ScraplingFetcher` 类

* 需要管理 session 生命周期

* 需要访问底层 Playwright page 对象

* **改动量：中等**

**方案B：使用 DynamicSession**

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, network_idle=True) as session:
    page = session.fetch(url)
    # 点击 Cookie 弹窗
    accept_btn = page.css('button#onetrust-accept-btn-handler')
    if accept_btn:
        await session.page.click('button#onetrust-accept-btn-handler')
```

**改动评估**：

* 需要重构为异步模式

* 需要管理 session 生命周期

* **改动量：较大**

**方案C：放弃 MSN 用例（简单方案）**

* MSN 是唯一需要 Cookie 点击的用例

* 改动成本与收益不成正比

* **改动量：零**

## 推荐方案

### 短期：方案C（放弃 MSN 用例）

* MSN 是唯一需要 Cookie 点击的用例

* 当前通过率已达 88.5%（23/26）

* 改动成本高，收益有限

### 长期：方案A（使用 StealthySession）

如果未来有更多网站需要 Cookie 点击，可以实现：

1. 在 `SiteConfig` 中添加 `cookie_click_selector` 参数
2. 重构 `ScraplingFetcher` 使用 `StealthySession`
3. 在 fetch 后检测并点击 Cookie 弹窗

```python
@dataclass
class SiteConfig:
    domain: str
    wait_for: Optional[str] = None
    content_selector: Optional[str] = None
    network_idle: bool = False
    cookie_click_selector: Optional[str] = None  # 新增
```

## 结论

| 方案                 | 可行性   | 改动量 | 推荐度  |
| ------------------ | ----- | --- | ---- |
| SiteConfig + click | ❌ 不可行 | -   | -    |
| StealthySession    | ✅ 可行  | 中等  | 长期推荐 |
| 放弃 MSN             | ✅ 可行  | 零   | 短期推荐 |

***

## 方案A 详细代码改动点

### 改动1：SiteConfig 添加 cookie\_click\_selector 参数

**文件**：`scripts/fetcher/site_config.py`

```python
@dataclass
class SiteConfig:
    domain: str
    wait_for: Optional[str] = None
    content_selector: Optional[str] = None
    network_idle: bool = False
    cookie_click_selector: Optional[str] = None  # 新增：Cookie弹窗按钮选择器

SITE_CONFIGS = [
    # ... 其他配置 ...
    SiteConfig(
        domain="*.msn.cn",
        wait_for="article",
        network_idle=True,
        cookie_click_selector="button#onetrust-accept-btn-handler",  # 新增
    ),
]
```

### 改动2：ScraplingFetcher 使用 StealthySession

**文件**：`scripts/fetcher/scrapling_fetcher.py`

**核心改动**：将 `_fetch_with_stealthy` 方法从使用 `StealthyFetcher.fetch()` 改为使用 `StealthySession`

```python
class ScraplingFetcher:
    def __init__(self):
        self._stealthy_session = None  # 改为 session
        self._fetcher = None

    def _fetch_with_stealthy(self, url: str, config: SiteConfig) -> FetchResult:
        from scrapling.fetchers import StealthySession

        # 创建 session
        with StealthySession(
            headless=True,
            network_idle=config.network_idle,
            disable_resources=False,
            hide_canvas=True,
            block_webrtc=True,
            google_search=True,
            solve_cloudflare=False,
            real_chrome=True,
            locale='zh-CN',
            timeout=15000,
            retries=2,
            retry_delay=2,
            adaptive=True,
        ) as session:
            # 第一次 fetch
            page = session.fetch(url, wait_for=config.wait_for)
            
            # 如果配置了 cookie_click_selector，点击 Cookie 弹窗
            if config.cookie_click_selector:
                cookie_btn = page.css(config.cookie_click_selector)
                if cookie_btn:
                    # 访问底层 Playwright page 进行点击
                    session.page.click(config.cookie_click_selector)
                    # 等待页面更新后重新获取
                    page = session.fetch(url, wait_for=config.wait_for)
            
            html_content = self._extract_html(page, config)
            title = _extract_title_from_html(page.html_content)
            return FetchResult(
                html=html_content,
                title=title,
                fetch_mode="stealth",
                success=True,
            )
```

### 改动点汇总

| 文件                     | 改动内容                          | 行数    |
| ---------------------- | ----------------------------- | ----- |
| `site_config.py`       | 添加 `cookie_click_selector` 字段 | \~3行  |
| `site_config.py`       | MSN 配置添加选择器                   | \~1行  |
| `scrapling_fetcher.py` | `__init__` 改为 session         | \~1行  |
| `scrapling_fetcher.py` | `_fetch_with_stealthy` 重构     | \~20行 |

**总改动量**：约 25 行代码

### 潜在问题

1. **Session 生命周期**：每次请求都创建/销毁 session，可能有性能开销
2. **Playwright page 访问**：需要确认 `session.page` 是否可访问（需查阅 Scrapling 源码）
3. **点击后等待**：点击后需要等待页面更新，可能需要额外的 `wait_for` 逻辑

### 验证结果

#### 验证步骤1: StealthySession 是否支持 Playwright page 访问

**结果**：✅ 成功

- `StealthySession` 没有 `page` 属性
- 但可以通过 `session.context.pages` 访问底层 Playwright 页面
- `session.context` 是 Playwright 的 `BrowserContext` 对象

```python
with StealthySession(headless=True) as session:
    page = session.fetch(url)
    pw_page = session.context.pages[0]  # 获取 Playwright 页面
    pw_page.click('button')  # 可以执行点击操作
```

#### 验证步骤2: 点击 Cookie 弹窗

**结果**：❌ 失败

**问题分析**：
1. MSN 页面在 headless 模式下**无法完全加载**
   - `article` 元素存在，但内容只有 22 字符（`; ; ; 继续阅读`）
   - 找不到任何 `button` 元素（Total buttons found: 0）
   - 找不到包含"同意"文本的元素

2. 非headless 模式同样失败
   - 同样找不到按钮元素
   - Cookie 弹窗可能是在 iframe 中，或者需要更复杂的 JavaScript 执行

**根本原因**：
- MSN 使用了复杂的 JavaScript 渲染，Cookie 弹窗可能在 iframe 中
- 或者 MSN 检测到自动化工具，阻止了页面完全加载
- 需要更深入的逆向工程才能解决

#### 验证步骤3: 结论

**方案A（使用 StealthySession）在技术上可行，但 MSN 网站有特殊限制**：

| 验证项 | 结果 | 说明 |
|--------|------|------|
| session.context.pages 访问 | ✅ 成功 | 可以获取 Playwright 页面 |
| page.click() 执行 | ✅ 成功 | 可以执行点击操作 |
| MSN 页面加载 | ❌ 失败 | headless 模式下页面无法完全加载 |
| Cookie 弹窗定位 | ❌ 失败 | 找不到 Cookie 按钮 |

**最终建议**：
1. **放弃 MSN 用例** - MSN 的反自动化机制过于复杂，投入产出比不划算
2. **保留 StealthySession 方案** - 未来其他网站可能需要 Cookie 点击功能
3. **今日头条问题已解决** - 通过 `network_idle=True` 参数

