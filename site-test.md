# 网页抓取测试文档

## 测试目标

验证 `scrapling_fetch.py` 脚本对各主流新闻网站的抓取能力，确保：
- 文章内容包含标题、正文内容
- 结果输出准确，避免缺失或错误信息
- 结构化内容输出，便于大模型理解
- 清除无用噪音，减少 token 消耗
- 绕过网站反爬机制，避免被封 IP

## 测试要求

- 仅在用户明确要求"全局测试"时执行全部测试列表

## 测试用法
```bash
uv run scripts/scrapling_fetch.py <url> 15000 --json
```

字符限制根据网页情况调整

## 测试输出格式

### JSON 输出示例

```json
{
  "ok": true,
  "url": "https://example.com",
  "final_url": "https://example.com/article",
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

## 测试结果保存
- 测试结果保存在 `output/` 目录下
- 文件命名格式：`{编号}_{域名}.md`（如 `01_mp.weixin.qq.com.md`）
- 每个测试结果文件包含以下内容：

| 字段 | 说明 |
|------|------|
| 编号 | 测试编号 |
| 原始 URL | 测试的目标 URL |
| 抓取状态 | 成功/失败 |
| mode | fetch mode|
|  解析器| parser |
| 文本长度 | content_length 值 |
| 质量评分 | 0-100 分 |
| 测试输出内容 | 完整的抓取内容 |

**质量评分标准（0-100分）：**
- 90-100：内容完整，噪音清除干净
- 70-89：内容基本完整，有少量噪音
- 50-69：内容有缺失或噪音较多
- 0-49：抓取失败或内容严重缺失


### 测试报告表格

| 编号 | 原始 URL | 抓取状态 | 文本长度  | 质量评分 | 变化 | 优化质量 |
|------|----------|----------|--------|----------|----------|----------|------------|----------------|
| 01 | https://... | 成功/失败  | 5000  | 0-100 | 是/否 | -10 |




对比测试时，根据编号和域名查找上一次测试结果

**变化**
  - 相较于上一次测试结果是否有变化
**优化质量百分比（负100-正100分）：**
  - 相较于上一次测试结果是否有优化，正优化或者负优化的

## 测试网站列表

每次测试后更新下面表格字段:
- 状态 - 是否已经通过，如果内容基本完整算通过
- 抓取质量评分 1-100
- 抓取质量简单评价

| 编号 | 网站域名 | URL                                                                                                                                                                                                                                                                                                              |
|------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 01 | mp.weixin.qq.com | https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw                                                                                                                                                                                                                                                                |
| 02 | finance.sina.com.cn | https://finance.sina.com.cn/roll/2025-09-19/doc-infrchxs4006271.shtml                                                                                                                                                                                                                                            |
| 05 | www.msn.cn | https://www.msn.cn/zh-cn/news/other/%E6%9D%8E%E8%BF%9E%E6%9D%B0%E7%AB%9F%E6%88%90-%E9%99%8C%E7%94%9F%E4%BA%BA-%E5%90%B4%E4%BA%AC%E8%B0%A2%E9%9C%86%E9%94%8B%E6%88%90%E6%9C%80%E5%90%8E%E4%B8%80%E4%BB%A3%E5%8A%9F%E5%A4%AB%E5%B7%A8%E6%98%9F-%E6%B1%9F%E6%B9%96%E8%B0%81%E6%9D%A5%E6%8E%A5%E6%A3%92/ar-AA1YB1E3  |
| 06 | www.sohu.com | https://www.sohu.com/a/996235269_121608032                                                                                                                                                                                                                                                                       |
| 07 | news.qq.com | https://news.qq.com/rain/a/20260313A08DDL00                                                                                                                                                                                                                                                                      |
| 08 | sports.huanqiu.com | https://sports.huanqiu.com/article/4QjG4cQdz1v                                                                                                                                                                                                                                                                   |
| 09 | www.guancha.cn | https://www.guancha.cn/sports/2026_03_13_809919.shtml                                                                                                                                                                                                                                                            |
| 10 | news.bjd.com.cn | https://news.bjd.com.cn/2026/03/13/11628598.shtml                                                                                                                                                                                                                                                                |
| 11 | news.sina.cn | https://news.sina.cn/gn/2026-03-13/detail-inhqvhtn4169536.d.html?vt=4                                                                                                                                                                                                                                            |
| 12 | www.globalpeople.com.cn | https://www.globalpeople.com.cn/n4/2026/0314/c305917-21644941.html                                                                                                                                                                                                                                               |
| 13 | www.chinanews.com.cn | https://www.chinanews.com.cn/ty/2026/03-13/10586350.shtml                                                                                                                                                                                                                                                        |
| 14 | www.36kr.com | https://www.36kr.com/p/2984752225886082                                                                                                                                                                                                                                                                          |
| 15 | www.nbd.com.cn | https://www.nbd.com.cn/articles/2025-10-17/4095107.html                                                                                                                                                                                                                                                          |
| 16 | news.qq.com | https://news.qq.com/rain/a/20260312A04DDQ00                                                                                                                                                                                                                                                                      |
| 17 | mp.weixin.qq.com | https://mp.weixin.qq.com/s?src=11&timestamp=1773504861&ver=6598&signature=FSs19V-Ql2lWLxlX-VpP4nC4ExvDySQ*kGgCISaYzeK95NOyGYvQdcgDJPimAepz4TPsH5wU7Xr*p9NXun4RYXJdq5gf6LS5OgdnA5skkuHKYxLwyGbbrzVa2mUaXzbW&new=1 |
| 18 | mp.weixin.qq.com | https://mp.weixin.qq.com/s?src=11&timestamp=1773504861&ver=6598&signature=GE-0ZZJTqAz1kgiq3CjcphvBPozwO8znBtUlsKQyqdaAsXfDkJ0SMf7HOdsMFHPkP-dOp60j6FXLSoUAtxCpyRrLgn4YOCYnszBPjUTtzDyQQBznjBzRWh3LYuy8MOH9&new=1                                                                                                                                                                                                                                                     |
| 19 | baijiahao.baidu.com | https://baijiahao.baidu.com/s?id=1859359368585426709&wfr=spider&for=pc                                                                                                                                                                                                                                           |
| 20 | baijiahao.baidu.com | https://baijiahao.baidu.com/s?id=1856155636617175508&wfr=spider&for=pc                                                                                                                                                                                                                                           |
| 21 | www.toutiao.com | https://www.toutiao.com/article/7617049061619581480/                                                                                                                                                                                                                                                             |
| 22 | news.mydrivers.com | https://news.mydrivers.com/1/1108/1108180.htm                                                                                                                                                                                                                                                                    |
| 23 | news.cctv.com | https://news.cctv.com/2026/03/14/ARTIKOxmS8y08Ezdt89y2I2z260314.shtml                                                                                                                                                                                                                                            |
| 24 | news.sina.com.cn | https://news.sina.com.cn/zx/gj/2026-03-14/doc-inhqwuuu3714268.shtml                                                                                                                                                                                                                                              |
| 25 | www.thepaper.cn | https://www.thepaper.cn/newsDetail_forward_32769323                                                                                                                                                                                                                                                              |
| 26 | military.people.com.cn | http://military.people.com.cn/n1/2025/1225/c1011-40631976.html                                                                                                                                                                                                                                                   |
| 27 | www.news.cn | https://www.news.cn/fortune/20260314/b04b8abad1b040f6ae04bb8623e00e50/c.html                                                                                                                                                                                                                                     |
| 28 | www.chinanews.com.cn | https://www.chinanews.com.cn/sh/2026/03-14/10586622.shtml                                                                                                                                                                                                                                                        |
| 29 | news.ifeng.com | https://news.ifeng.com/c/8rUozrIUp80                                                                                                                                                                                                                                                                             |
| 30 | www.bilibili.com | https://www.bilibili.com/opus/1175833574604013571                                                                                                                                                                                                                                                                |
| 31 | www.huxiu.com | https://www.huxiu.com/article/4842060.html                                                                                                                                                                                                                                                                       |
