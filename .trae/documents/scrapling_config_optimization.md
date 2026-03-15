# Scrapling 配置优化计划

## 一、问题根因分析

### 为什么 timeout=30000 (30秒) 却耗时 128-135 秒？

**关键发现**：通过分析 Scrapling 源码，发现 `solve_cloudflare=True` 是超时的根本原因。

#### 源码分析

**1.** **`_wait_for_networkidle`** **方法**（\_base.py:134-139）：

```python
@staticmethod
def _wait_for_networkidle(page: Page | Frame, timeout: Optional[int] = None):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except (PlaywrightError, Exception):
        pass  # 捕获所有异常，静默继续
```

**2.** **`_cloudflare_solver`** **方法**（\_stealth.py:110-185）：

```python
def _cloudflare_solver(self, page: Page) -> None:
    self._wait_for_networkidle(page, timeout=5000)  # 5秒超时
    challenge_type = self._detect_cloudflare(...)
    
    if not challenge_type:
        log.error("No Cloudflare challenge found.")  # 这就是日志里看到的！
        return None
    
    # ... 处理 Cloudflare 验证码 ...
```

**3. fetch 方法流程**（\_stealth.py:233-243）：

```python
first_response = page.goto(url, referer=referer)
self._wait_for_page_stability(page, params.load_dom, params.network_idle)

if params.solve_cloudflare:
    self._cloudflare_solver(page)  # 这里可能耗时很长！
    self._wait_for_page_stability(page, params.load_dom, params.network_idle)
```

#### 超时原因

1. **`solve_cloudflare=True`** 导致每次请求都尝试检测 Cloudflare
2. `_cloudflare_solver` 首先调用 `_wait_for_networkidle(page, timeout=5000)` 等待5秒
3. 如果没有检测到 Cloudflare，输出 `ERROR: No Cloudflare challenge found.` 并返回
4. 之后再次调用 `_wait_for_page_stability`，如果 `network_idle=True`，又会等待网络空闲
5. `network_idle=True` 时，`_wait_for_networkidle` 使用页面默认超时（30秒）
6. 如果页面有持续的网络活动（广告、分析脚本等），会等待满30秒才超时返回

**总耗时估算**：

* 页面加载 + load 状态：\~5秒

* network\_idle 第一次等待（超时）：30秒

* Cloudflare solver 的 network\_idle：5秒

* network\_idle 第二次等待（超时）：30秒

* 其他操作：\~5秒

* **总计：约 75-100 秒**

这解释了 guancha.cn (128秒) 和 news.sina.cn (135秒) 的超时现象。

***

## 二、完整参数列表

### PlaywrightSession 基础参数

| 参数                    | 类型                      | 默认值        | 说明               |
| --------------------- | ----------------------- | ---------- | ---------------- |
| `headless`            | bool                    | True       | 无头模式             |
| `network_idle`        | bool                    | False      | 等待网络空闲           |
| `disable_resources`   | bool                    | False      | 禁用图片/CSS/字体等资源   |
| `load_dom`            | bool                    | True       | 等待DOM加载完成        |
| `wait_selector`       | Optional\[str]          | None       | 等待特定CSS选择器       |
| `wait_selector_state` | str                     | "attached" | 选择器等待状态          |
| `wait`                | int/float               | 0          | 额外等待时间（毫秒）       |
| `timeout`             | int/float               | 30000      | 页面操作超时（毫秒）       |
| `extra_headers`       | Optional\[Dict]         | None       | 额外请求头            |
| `useragent`           | Optional\[str]          | None       | 自定义User-Agent    |
| `cookies`             | Optional\[Sequence]     | None       | 设置Cookie         |
| `proxy`               | Optional\[str/Dict]     | None       | 代理配置             |
| `proxy_rotator`       | Optional\[ProxyRotator] | None       | 代理轮换器            |
| `blocked_domains`     | Optional\[Set\[str]]    | None       | 阻止的域名列表          |
| `locale`              | Optional\[str]          | 系统默认       | 语言区域             |
| `timezone_id`         | Optional\[str]          | 系统默认       | 时区               |
| `google_search`       | bool                    | True       | 设置Google referer |
| `real_chrome`         | bool                    | False      | 使用真实Chrome       |
| `init_script`         | Optional\[str]          | None       | 页面初始化脚本          |
| `page_action`         | Optional\[Callable]     | None       | 页面回调函数           |
| `retries`             | int                     | 1          | 重试次数             |
| `retry_delay`         | int/float               | 1          | 重试延迟（秒）          |

### StealthSession 特有参数

| 参数                 | 类型   | 默认值   | 说明               |
| ------------------ | ---- | ----- | ---------------- |
| `allow_webgl`      | bool | True  | 允许WebGL          |
| `hide_canvas`      | bool | False | 隐藏Canvas指纹       |
| `block_webrtc`     | bool | False | 阻止WebRTC泄露IP     |
| `solve_cloudflare` | bool | False | 自动解决Cloudflare验证 |

***

## 三、优化建议

### 1. 关闭 `solve_cloudflare`（关键！）

**原因**：

* 大多数新闻网站没有 Cloudflare 保护

* `solve_cloudflare=True` 会导致每次请求都尝试检测和处理 Cloudflare

* 即使没有 Cloudflare，也会额外等待 5 秒 + 日志输出

**建议**：设置 `solve_cloudflare=False`，仅在明确需要时开启

### 2. 关闭 `network_idle`

**原因**：

* `network_idle=True` 会等待网络完全空闲

* 新闻网站通常有大量广告和分析脚本持续发送请求

* 网络永远不会空闲，导致每次都等待超时

**建议**：设置 `network_idle=False`

### 3. 启用 `disable_resources`

**原因**：

* 新闻抓取只需要HTML文本

* 禁用图片、CSS、字体、媒体等资源可大幅加速

* 减少网络请求，降低被检测风险

**建议**：设置 `disable_resources=True`

### 4. 降低 `timeout`

**原因**：

* 30秒太长，失败时等待时间过长

* 新闻页面通常 5-10 秒内可完成加载

**建议**：设置 `timeout=15000` (15秒)

### 5. 添加 `blocked_domains`

**原因**：

* 阻止广告和分析域名，加速加载

* 减少不必要的网络请求

**建议**：配置常见广告域名黑名单

### 6. 添加重试机制

**建议**：设置 `retries=2, retry_delay=2`

***

## 四、优化后配置

```python
def _fetch_with_stealthy(self, url: str) -> FetchResult:
    from scrapling.fetchers import StealthyFetcher

    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=False,
        disable_resources=True,
        hide_canvas=True,
        block_webrtc=True,
        google_search=False,
        solve_cloudflare=False,
        real_chrome=True,
        locale='zh-CN',
        timeout=15000,
        retries=2,
        retry_delay=2,
        adaptive=True,
    )
    html = page.html_content
    return FetchResult(
        html=html,
        final_url=page.url,
        title=_extract_title_from_html(html),
        fetch_mode="stealth",
        success=True,
    )

def _fetch_with_fetcher(self, url: str) -> FetchResult:
    from scrapling.fetchers import Fetcher

    fetcher = Fetcher()
    page = fetcher.get(
        url,
        stealthy_headers=True,
        adaptive=True,
        timeout=15,
    )
    html = page.html_content
    return FetchResult(
        html=html,
        final_url=page.url,
        title=_extract_title_from_html(html),
        fetch_mode="fetcher",
        success=True,
    )
```

***

## 五、实施步骤

1. **删除模块级配置常量** `STEALTHY_FETCHER_CONFIG` 和 `FETCHER_CONFIG`
2. **修改** **`_fetch_with_stealthy`** **方法**：直接在方法内配置参数
3. **修改** **`_fetch_with_fetcher`** **方法**：直接在方法内配置参数
4. **测试验证**：运行前10条测试用例验证优化效果

***

## 六、预期效果

| 指标             | 优化前      | 优化后   |
| -------------- | -------- | ----- |
| 正常页面抓取时间       | 5-30秒    | 2-8秒  |
| 超时页面抓取时间       | 128-135秒 | 15秒内  |
| 资源加载量          | 全部资源     | 仅HTML |
| Cloudflare检测开销 | 每次请求+5秒  | 无     |

***

## 七、注意事项

### 何时启用 `solve_cloudflare`

如果遇到真正的 Cloudflare 保护页面（如 `challenges.cloudflare.com`），可以：

1. 单独为该请求启用 `solve_cloudflare=True`
2. 或者在检测到 Cloudflare 时自动重试并启用

### `network_idle` 的正确使用场景

`network_idle=True` 适用于：

* 动态加载内容的页面（SPA）

* 需要等待 AJAX 请求完成的场景

对于新闻网站，通常 `load_dom=True` 已经足够。
