# 网站测试 Skill 创建计划

## 目标

将 `site-test.md` 中的测试流程转化为可复用的 Skill，采用**大模型参与评估**的交互式测试流程。

## 测试流程设计

```
┌─────────────────────────────────────────────────────────────────┐
│  1. site_test.py --fetch                                       │
│     读取 cases.json → 过滤需要测试的用例 → 执行抓取 → 输出结果    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. 大模型评估                                                  │
│     查看抓取结果 → 判断状态、质量评分、质量评价                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. site_test.py --save-result                                 │
│     保存测试结果到 output/{编号}_{域名}.md                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. site_test.py --update-case                                 │
│     更新 cases.json 中的状态、质量评分、质量评价                  │
└─────────────────────────────────────────────────────────────────┘
```

## 实现步骤

### 步骤 1：创建测试用例 JSON 文件

**文件路径**: `cases.json`

```json
{
  "last_updated": "2026-03-15",
  "cases": [
    {
      "id": "01",
      "domain": "mp.weixin.qq.com",
      "status": "passed",
      "quality_score": 95,
      "quality_comment": "内容完整，噪音清除干净",
      "url": "https://mp.weixin.qq.com/s/FrWhkYKonLX3ZuD6nDhXpw"
    }
  ]
}
```

**状态枚举值**：

| 枚举值       | 显示文本  | 说明   |
| --------- | ----- | ---- |
| `passed`  | ✅ 通过  | 跳过测试 |
| `failed`  | ❌ 失败  | 需要测试 |
| `timeout` | ⚠️ 超时 | 需要测试 |
| `pending` | (空)   | 需要测试 |

### 步骤 2：创建测试脚本

**文件路径**: `scripts/site_test.py`

**命令设计**：

```bash
# 1. 执行测试（读取用例，过滤已通过的，执行抓取）
uv run scripts/site_test.py --fetch [--id 02,05,08] [--all]

# 2. 保存测试结果到 output/
uv run scripts/site_test.py --save-result --id 02 --status failed --score 10 --comment "内容全为噪音" --content "抓取内容..."

# 3. 更新 cases.json
uv run scripts/site_test.py --update-case --id 02 --status failed --score 10 --comment "内容全为噪音"
```

**输出格式**（--fetch 模式）：

```json
{
  "id": "02",
  "domain": "finance.sina.com.cn",
  "url": "https://...",
  "fetch_result": {
    "ok": true,
    "title": "文章标题",
    "content_length": 5000,
    "fetch_mode": "stealth",
    "parser": "trafilatura",
    "total_duration": 5.56,
    "content": "正文内容..."
  }
}
```

### 步骤 3：创建测试 Skill

**文件路径**: `.trae/skills/site-test/SKILL.md`

Skill 描述包含：

* 测试流程说明

* 命令用法

* 质量评分标准

* 大模型评估指南

### 步骤 4：测试结果文件格式

**文件路径**: `output/{编号}_{域名}.md`

```markdown
## 测试结果
- **编号**：02  
- **原始 URL**：https://...  
- **抓取状态**：❌ 失败  
- **抓取模式**：stealth  
- **解析器**：trafilatura  
- **文本长度**：150

## 质量评分：10 分

## 问题分析
Trafilatura 解析失败，内容全为噪音

## 优化建议
尝试使用 scrapling 解析器
```

**注意**：文件中使用 emoji 显示状态，但脚本参数使用枚举值。

### 步骤 5：删除 site-test.md

将 `site-test.md` 中的内容迁移到 `SKILL.md` 后，删除该文件。

迁移内容：
- 测试目标
- 质量评分标准
- 测试输出格式
- 测试结果保存格式

## 文件清单

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| 创建 | `cases.json` | 测试用例数据 |
| 创建 | `.trae/skills/site-test/SKILL.md` | Skill 描述（包含测试目标、评分标准等） |
| 创建 | `scripts/site_test.py` | 测试脚本（多命令模式） |
| 删除 | `site-test.md` | 内容已迁移到 SKILL.md |

## Skill 调用流程示例

```
用户: 测试编号 02 的网站

大模型:
1. 调用 site_test.py --fetch --id 02
2. 查看抓取结果，评估质量
3. 调用 site_test.py --save-result --id 02 --status failed --score 10 --comment "..."
4. 调用 site_test.py --update-case --id 02 --status failed --score 10 --comment "..."
```

