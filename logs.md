# 抓取问题日志

## 2026-03-15 测试记录

### finance.sina.com.cn

**时间**: 2026-03-15 20:58
**原始 URL**: https://finance.sina.com.cn/roll/2025-09-19/doc-infrchxs4006271.shtml
**抓取状态**: 失败
**抓取模式**: stealth
**解析器**: trafilatura
**文本长度**: 0
**问题描述**: Trafilatura 解析失败，无法识别正文区域

**原因分析**:
- 新浪财经页面结构复杂，正文区域可能使用了特殊的 HTML 结构
- 页面包含大量动态加载内容

**优化方案**:
- 分析页面 HTML 结构，找到正文区域的选择器
- 在 spec/finance.sina.com.cn.py 中添加自定义解析逻辑
- 尝试使用 Scrapling 解析器作为备选

---

### www.msn.cn

**时间**: 2026-03-15 19:30
**原始 URL**: https://www.msn.cn/zh-cn/news/other/...
**抓取状态**: 失败
**抓取模式**: stealth
**解析器**: trafilatura
**文本长度**: 2490
**问题描述**: 抓取内容全是 Cookie 政策文本，正文缺失；抓取耗时 131.8 秒

**原因分析**:
- MSN 网站有 Cookie 同意弹窗，StealthyFetcher 没有正确处理
- 页面需要等待 Cookie 弹窗关闭后才能获取正文

**优化方案**:
- 在 ScraplingFetcher 中添加等待机制
- 添加自动关闭 Cookie 弹窗的逻辑
- 设置更短的超时时间

---

### sports.huanqiu.com

**时间**: 2026-03-15 19:32
**原始 URL**: https://sports.huanqiu.com/article/4QjG4cQdz1v
**抓取状态**: 失败
**抓取模式**: stealth
**解析器**: trafilatura
**文本长度**: 101
**问题描述**: 抓取内容是 AdBlock 检测提示，正文缺失

**原因分析**:
- 环球网检测到模拟浏览器行为，触发了反爬机制
- 页面检测到 AdBlock 后隐藏了正文内容

**优化方案**:
- 尝试不同的 User-Agent
- 在请求中添加特定的 headers 绕过检测
- 使用真实浏览器环境

---

### www.guancha.cn / news.sina.cn

**时间**: 2026-03-15 19:34-19:38
**抓取状态**: 成功但超时
**问题描述**: 抓取成功但耗时超过 2 分钟

**原因分析**:
- StealthyFetcher 默认等待时间过长
- 页面可能有大量动态加载内容

**优化方案**:
- 设置合理的超时时间限制（30秒）
- 优化等待策略，减少不必要的等待
