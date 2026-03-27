---
title: AI 每日简报 Skill (ai-daily-briefing)
type: knowledge-note
created: 2026-03-16T06:25:46.176Z
tags: ["ai", "machine-learning", "automation", "skills", "github", "arxiv", "huggingface"]
---

# AI 每日简报 Skill (ai-daily-briefing)

# AI 每日简报 Skill

## 概述

**名称：** ai-daily-briefing

**描述：** AI 每日简报生成工具，自动从 GitHub、ArXiv 和 Hugging Face 收集最新 AI 项目、论文和模型，生成格式化的每日简报。

---

## 快速开始

生成一份 AI 每日简报：

```bash
python scripts/generate_briefing.py
```

输出默认保存为 `ai-daily-briefing.md`。

---

## 自定义选项

```bash
# 指定输出文件
python scripts/generate_briefing.py -o my-briefing.md

# 调整各数据源的数量
python scripts/generate_briefing.py --github-count 3 --arxiv-count 10 --hf-count 5

# 输出 JSON 格式
python scripts/generate_briefing.py --json -o briefing.json
```

---

## 数据源说明

### GitHub 热门项目
- 收集最近 7 天内创建的 AI/ML 相关仓库
- 按星标数排序
- 包含：项目名称、描述、语言、星标数

### ArXiv 最新论文
- 查询 cs.AI、cs.LG、cs.CL、cs.CV 类别
- 按提交时间倒序
- 包含：标题、作者、摘要、分类

### Hugging Face 热门模型
- 按下载量排序
- 包含：模型 ID、任务类型、下载量、标签

---

## 核心脚本

### 1. collect_github.py - 收集 GitHub 热门项目

```python
#!/usr/bin/env python3
"""
Collect trending AI/ML repositories from GitHub
"""

import requests
import json
from datetime import datetime

GITHUB_TRENDING_URL = "https://api.github.com/search/repositories"

AI_KEYWORDS = ["machine learning", "deep learning", "AI", "LLM", "transformer", "neural network"]

def collect_trending_ai_repos(limit=10, days=7):
    """
    Collect trending AI repositories from GitHub

    Args:
        limit: Number of repos to return
        days: Number of days to look back

    Returns:
        List of trending repos with metadata
    """
    date_filter = f">{datetime.now().strftime('%Y-%m-%d')}"
    repos = []

    for keyword in AI_KEYWORDS[:2]:  # Limit to avoid rate limiting
        params = {
            "q": f"{keyword} language:python created:{date_filter}",
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }

        try:
            response = requests.get(GITHUB_TRENDING_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                repos.append({
                    "name": item["full_name"],
                    "url": item["html_url"],
                    "stars": item["stargazers_count"],
                    "description": item["description"] or "No description",
                    "language": item.get("language", "Unknown"),
                    "created_at": item["created_at"]
                })
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")

    # Remove duplicates and sort by stars
    unique_repos = {r["name"]: r for r in repos}.values()
    return sorted(unique_repos, key=lambda x: x["stars"], reverse=True)[:limit]
```

### 2. collect_arxiv.py - 收集 ArXiv 最新论文

```python
#!/usr/bin/env python3
"""
Collect latest AI/ML papers from ArXiv
"""

import requests
import feedparser
import json
from datetime import datetime, timedelta

ARXIV_API_URL = "http://export.arxiv.org/api/query"

# AI/ML relevant categories
ARXIV_CATEGORIES = [
    "cs.AI",  # Artificial Intelligence
    "cs.LG",  # Machine Learning
    "cs.CL",  # Computation and Language (NLP)
    "cs.CV",  # Computer Vision
]

def collect_recent_papers(days=1, limit=10):
    """
    Collect recent AI/ML papers from ArXiv

    Args:
        days: Number of days to look back
        limit: Maximum number of papers to return

    Returns:
        List of papers with metadata
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Build query for AI/ML categories
    category_query = " OR ".join([f"cat:{cat}" for cat in ARXIV_CATEGORIES])

    params = {
        "search_query": category_query,
        "start": 0,
        "max_results": limit * 2,  # Fetch more to filter
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    papers = []

    try:
        response = requests.get(ARXIV_API_URL, params=params, timeout=30)
        response.raise_for_status()

        # Parse Atom feed
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            # Parse authors
            authors = [author.name for author in entry.authors[:5]]  # Limit to 5 authors
            if len(entry.authors) > 5:
                authors.append(f"et al. ({len(entry.authors)} authors total)")

            papers.append({
                "title": entry.title,
                "authors": authors,
                "summary": entry.summary.split("\n")[0][:300] + "...",  # First paragraph
                "url": entry.link,
                "published": entry.published,
                "categories": [tag.term for tag in entry.tags if tag.term.startswith("cs.")],
                "arxiv_id": entry.id.split("/abs/")[-1]
            })

            if len(papers) >= limit:
                break

    except Exception as e:
        print(f"Error fetching ArXiv data: {e}")

    return papers
```

### 3. collect_huggingface.py - 收集 Hugging Face 热门模型

```python
#!/usr/bin/env python3
"""
Collect trending models from Hugging Face
"""

import requests
import json
from datetime import datetime

HUGGINGFACE_API_URL = "https://huggingface.co/api/models"

def collect_trending_models(limit=10):
    """
    Collect trending AI models from Hugging Face

    Args:
        limit: Number of models to return

    Returns:
        List of trending models with metadata
    """
    models = []

    # Hugging Face API parameters
    params = {
        "limit": limit * 2,  # Fetch more for filtering
        "sort": "downloads",
        "direction": "-1"
    }

    try:
        response = requests.get(HUGGINGFACE_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        for model in data:
            # Filter for AI/ML models
            model_id = model.get("id", "")
            if not model_id:
                continue

            models.append({
                "model_id": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "created_at": model.get("createdAt", ""),
                "tags": model.get("tags", [])[:5],  # Limit tags
                "pipeline_tag": model.get("pipeline_tag", "Unknown")
            })

            if len(models) >= limit:
                break

    except Exception as e:
        print(f"Error fetching Hugging Face data: {e}")

    return models
```

### 4. generate_briefing.py - 生成简报

```python
#!/usr/bin/env python3
"""
Generate AI Daily Briefing by collecting data from multiple sources
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

# Import collectors
import sys
sys.path.append(Path(__file__).parent)
from collect_github import collect_trending_ai_repos
from collect_arxiv import collect_recent_papers
from collect_huggingface import collect_trending_models

def generate_briefing_markdown(github_repos, arxiv_papers, hf_models, date=None):
    """
    Generate a markdown briefing from collected data

    Args:
        github_repos: List of trending GitHub repos
        arxiv_papers: List of recent ArXiv papers
        hf_models: List of trending Hugging Face models
        date: Date for the briefing (defaults to today)

    Returns:
        Markdown formatted briefing
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    md = f"""# AI 每日简报

> 生成时间：{date}
> 数据来源：GitHub, ArXiv, Hugging Face

---

## 📈 GitHub 热门 AI 项目

"""

    # GitHub section
    if github_repos:
        for i, repo in enumerate(github_repos, 1):
            md += f"""### {i}. [{repo['name']}]({repo['url']}) ⭐ {repo['stars']}

**描述：** {repo['description']}

**语言：** {repo['language']} | **创建时间：** {repo['created_at']}

---

"""
    else:
        md += "暂无数据\n\n---\n\n"

    # ArXiv section
    md += """## 📚 ArXiv 最新论文

"""

    if arxiv_papers:
        for i, paper in enumerate(arxiv_papers, 1):
            authors_str = ", ".join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors_str += f" et al."

            md += f"""### {i}. {paper['title']}

**作者：** {authors_str}

**摘要：** {paper['summary']}

**链接：** [{paper['arxiv_id']}]({paper['url']}) | **分类：** {", ".join(paper['categories'][:2])}

---

"""
    else:
        md += "暂无数据\n\n---\n\n"

    # Hugging Face section
    md += """## 🤗 Hugging Face 热门模型

"""

    if hf_models:
        for i, model in enumerate(hf_models, 1):
            md += f"""### {i}. [{model['model_id']}]({model['url']})

**类型：** {model['pipeline_tag']} | **下载量：** {model['downloads']:,} | **点赞：** {model['likes']}

**标签：** {", ".join(model['tags'][:5])}

---

"""
    else:
        md += "暂无数据\n\n---\n\n"

    md += f"""
---

*本简报由 AI 自动生成，数据收集时间：{date}*
"""

    return md

def save_briefing(markdown_content, output_path):
    """Save briefing to file"""
    Path(output_path).write_text(markdown_content, encoding="utf-8")
    print(f"✅ Briefing saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate AI Daily Briefing")
    parser.add_argument("--output", "-o", default="ai-daily-briefing.md", help="Output file path")
    parser.add_argument("--github-count", type=int, default=5, help="Number of GitHub repos")
    parser.add_argument("--arxiv-count", type=int, default=5, help="Number of ArXiv papers")
    parser.add_argument("--hf-count", type=int, default=5, help="Number of HF models")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")

    args = parser.parse_args()

    print("🔍 Collecting data from GitHub...")
    github_repos = collect_trending_ai_repos(limit=args.github_count)
    print(f"✓ Found {len(github_repos)} trending repos")

    print("🔍 Collecting data from ArXiv...")
    arxiv_papers = collect_recent_papers(limit=args.arxiv_count)
    print(f"✓ Found {len(arxiv_papers)} recent papers")

    print("🔍 Collecting data from Hugging Face...")
    hf_models = collect_trending_models(limit=args.hf_count)
    print(f"✓ Found {len(hf_models)} trending models")

    if args.json:
        output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "github": github_repos,
            "arxiv": arxiv_papers,
            "huggingface": hf_models
        }
        Path(args.output).write_text(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"✅ JSON briefing saved to: {args.output}")
    else:
        markdown_content = generate_briefing_markdown(github_repos, arxiv_papers, hf_models)
        save_briefing(markdown_content, args.output)

if __name__ == "__main__":
    main()
```

---

## 仅收集特定数据源

如需只收集特定源的数据，直接运行对应脚本：

```bash
python scripts/collect_github.py      # 仅 GitHub
python scripts/collect_arxiv.py       # 仅 ArXiv
python scripts/collect_huggingface.py # 仅 Hugging Face
```

---

## 依赖安装

```bash
pip install requests feedparser
```

---

## 定时任务

使用 cron 每天自动生成简报：

```bash
# 每天早上 8 点生成
0 8 * * * cd /path/to/skill && python scripts/generate_briefing.py
```

---

## Tags

#ai #machine-learning #automation #skills #github #arxiv #huggingface



## Related Notes

- [[LangGraph State对象设计指南|LangGraph State对象设计指南.md]]
- [[SAM3模型分析与部署|SAM3模型分析与部署.md]]
- [[个人博客内容总结|个人博客内容总结.md]]


---
*Created: 3/16/2026, 2:25:46 PM*
