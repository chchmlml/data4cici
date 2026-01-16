---
name: exam-paper-crawler
description: 试卷爬取器，用于从指定网站（如shijuan1.com）爬取试卷详情页信息，并将试卷名称和链接保存为美观可读的markdown格式文件。
---

# 试卷爬取器

## 概述

试卷爬取器是一个用于自动爬取试卷网站上的试卷信息的工具，可以从指定的网址（默认使用https://www.shijuan1.com/）抓取试卷的名称和详情页链接，并将这些信息整理成结构化的markdown文件，方便用户查看和使用。

## 快速开始

### 使用方法

1. **安装依赖**
   ```bash
   pip install requests beautifulsoup4
   ```

2. **运行脚本**
   ```bash
   # 使用默认网址爬取
   python3 scripts/crawler.py
   
   # 使用指定网址爬取
   python3 scripts/crawler.py --url https://www.shijuan1.com/
   
   # 指定输出文件名
   python3 scripts/crawler.py --output my_papers.md
   ```

### 命令参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--url` | 目标网站URL | https://www.shijuan1.com/ |
| `--output` | 输出markdown文件名 | papers.md |

## 功能说明

### 1. 网页内容获取
- 使用requests库发送HTTP请求，获取目标网站的HTML内容
- 支持自定义User-Agent，模拟浏览器访问
- 处理超时和HTTP错误

### 2. 试卷信息提取
- 使用BeautifulSoup4解析HTML内容
- 根据页面结构查找试卷详情页链接
- 过滤和去重，确保只提取有效链接

### 3. 结果保存
- 将提取的试卷信息保存为markdown格式
- 使用表格布局，包含序号、试卷名称和详情链接
- 支持中文编码，确保标题显示正常

## 输出示例

生成的markdown文件示例：

```markdown
# 试卷列表

共找到 **25** 份试卷

| 序号 | 试卷名称 | 详情链接 |
|------|----------|----------|
| 1 | 2023年高考新课标卷（五省）政治 | [https://www.shijuan1.com/html/31864.html](https://www.shijuan1.com/html/31864.html) |
| 2 | 2023年高考全国甲卷语文 | [https://www.shijuan1.com/html/31863.html](https://www.shijuan1.com/html/31863.html) |
| 3 | 2023年高考全国乙卷数学（理） | [https://www.shijuan1.com/html/31862.html](https://www.shijuan1.com/html/31862.html) |
```

## 资源

### scripts/
包含可执行的Python脚本：

- `crawler.py` - 主爬虫脚本，用于爬取试卷信息并保存为markdown文件

### references/
包含参考文档和说明：

- `api_reference.md` - API参考文档（示例）

### assets/
包含示例资源文件：

- `example_asset.txt` - 示例资源文件（示例）

---

**注意：** 请遵守网站的robots.txt规则，合理使用爬虫工具，避免对目标网站造成过大的访问压力。
