#!/usr/bin/env python3
"""
试卷爬取器 - 从指定网站爬取试卷信息并保存为markdown格式

Usage:
    crawler.py [--url <url>] [--grade <grade>] [--subject <subject>] [--output <output-file>]

Examples:
    # 爬取一年级数学试卷
    crawler.py --grade 1 --subject math
    
    # 爬取二年级语文试卷并指定输出文件名
    crawler.py --grade 2 --subject chinese --output grade2_chinese.md
    
    # 使用自定义URL
    crawler.py --url https://www.shijuan1.com/a/sjsx1/ --output custom.md
"""

import argparse
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time

# 科目映射
subject_map = {
    'math': 'sx',  # 数学
    'chinese': 'yw',  # 语文
    'english': 'yy',  # 英语
    'physics': 'wl',  # 物理
    'chemistry': 'hx',  # 化学
    'biology': 'sw',  # 生物
    'politics': 'zz',  # 政治
    'history': 'ls',  # 历史
    'geography': 'dl'  # 地理
}


def parse_args():
    parser = argparse.ArgumentParser(description='试卷爬取器')
    parser.add_argument('--url', help='目标网站URL')
    parser.add_argument('--grade', type=int, help='年级（1-9）')
    parser.add_argument('--subject', choices=subject_map.keys(), help='科目（math/chinese/english/physics/chemistry/biology/politics/history/geography）')
    parser.add_argument('--output', help='输出markdown文件名')
    parser.add_argument('--page-range', type=str, help='分页范围，如 "1-99"')
    parser.add_argument('--page-format', help='分页URL格式，如 "list_112_{page}.html"')
    return parser.parse_args()


def fetch_html(url):
    """获取网页HTML内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果响应状态码不是200，抛出HTTPError异常
        
        # 尝试不同的编码
        encodings = ['utf-8', 'gb2312', 'gbk', 'big5']
        html = None
        
        for encoding in encodings:
            try:
                response.encoding = encoding
                html = response.text
                # 检查是否有明显的乱码特征
                if '��' not in html:
                    break
            except:
                continue
        
        if html is None:
            # 如果所有编码都失败，使用默认
            html = response.text
            print("警告: 无法正确解析网页编码，可能存在乱码")
        
        return html
    except requests.RequestException as e:
        print(f"获取网页失败: {e}")
        return None


def extract_papers(html, base_url):
    """从HTML中提取试卷信息"""
    papers = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找试卷链接，根据shijuan1.com的页面结构
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        text = a_tag.get_text(strip=True)
        
        # 过滤出试卷详情页链接
        if re.search(r'\d+\.html$', href) and text:
            # 构造完整URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = base_url.split('/')[0] + '//' + base_url.split('/')[2] + href
            else:
                # 检查链接是否已经包含完整路径
                if '/a/' in href:
                    full_url = base_url.split('/')[0] + '//' + base_url.split('/')[2] + '/' + href
                else:
                    full_url = base_url.rstrip('/') + '/' + href
            
            papers.append({
                'title': text,
                'url': full_url
            })
    
    # 去重
    unique_papers = []
    seen_urls = set()
    for paper in papers:
        if paper['url'] not in seen_urls:
            seen_urls.add(paper['url'])
            unique_papers.append(paper)
    
    return unique_papers


def extract_pagination_info(html):
    """提取分页信息，包括最大页数"""
    soup = BeautifulSoup(html, 'html.parser')
    max_page = 1
    
    # 尝试直接找到最大页数
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        text = a_tag.get_text(strip=True)
        
        # 查找类似 "尾页" 的链接
        if '尾页' in text or '最后一页' in text:
            if re.search(r'index_(\d+)\.html$', href):
                max_page = int(re.search(r'index_(\d+)\.html$', href).group(1))
                break
        
        # 查找数字链接，找到最大的页码
        if text.isdigit():
            if re.search(r'index_\d+\.html$', href):
                page_num = int(text)
                if page_num > max_page:
                    max_page = page_num
    
    return max_page


def extract_all_papers(start_url, page_range=None, page_format=None):
    """提取所有页面的试卷信息"""
    all_papers = []
    seen_urls = set()
    
    # 确定要爬取的页面范围
    if page_range:
        # 解析页面范围，如 "1-99"
        start_page, end_page = map(int, page_range.split('-'))
        print(f"使用自定义分页范围: {start_page}-{end_page}")
    else:
        # 自动检测页面范围
        print(f"正在爬取第1页: {start_url}")
        html = fetch_html(start_url)
        if not html:
            return []
        
        # 提取第一页的试卷
        papers = extract_papers(html, start_url)
        all_papers.extend(papers)
        
        # 提取最大页数
        max_page = extract_pagination_info(html)
        print(f"发现最大页数: {max_page}")
        
        if max_page <= 1:
            print("只有1页，无需继续爬取")
            # 去重
            unique_papers = []
            seen_paper_urls = set()
            for paper in all_papers:
                if paper['url'] not in seen_paper_urls:
                    seen_paper_urls.add(paper['url'])
                    unique_papers.append(paper)
            return unique_papers
        
        start_page = 2
        end_page = max_page
    
    # 构造所有分页URL
    base_url = start_url.rstrip('/')
    
    for page_num in range(start_page, end_page + 1):
        # 构造分页URL
        if page_format:
            # 使用自定义分页格式
            page_suffix = page_format.replace('{page}', str(page_num))
            page_url = f"{base_url}/{page_suffix}"
        else:
            # 使用默认分页格式
            page_url = f"{base_url}/index_{page_num}.html"
        
        # 避免重复爬取同一页面
        if page_url in seen_urls:
            continue
        seen_urls.add(page_url)
        
        print(f"正在爬取第{page_num}页: {page_url}")
        
        # 获取分页内容
        page_html = fetch_html(page_url)
        if not page_html:
            continue
        
        # 提取当前分页的试卷
        page_papers = extract_papers(page_html, start_url)
        all_papers.extend(page_papers)
        
        # 避免爬取过快
        time.sleep(1)
    
    # 去重
    unique_papers = []
    seen_paper_urls = set()
    for paper in all_papers:
        if paper['url'] not in seen_paper_urls:
            seen_paper_urls.add(paper['url'])
            unique_papers.append(paper)
    
    return unique_papers


def save_to_markdown(papers, output_file):
    """将试卷信息保存为markdown格式"""
    if not papers:
        print("没有找到试卷信息")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入标题
            f.write("# 试卷列表\n\n")
            
            # 写入试卷数量
            f.write(f"共找到 **{len(papers)}** 份试卷\n\n")
            
            # 写入试卷列表，使用表格格式
            f.write("| 序号 | 试卷名称 | 详情链接 |\n")
            f.write("|------|----------|----------|\n")
            
            for i, paper in enumerate(papers, 1):
                f.write(f"| {i} | {paper['title']} | [{paper['url']}]({paper['url']}) |\n")
        
        print(f"试卷信息已保存到: {output_file}")
        return True
    except IOError as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    args = parse_args()
    
    print(f"调试信息 - 参数:")
    print(f"  --url: {args.url}")
    print(f"  --grade: {args.grade}")
    print(f"  --subject: {args.subject}")
    
    # 处理URL生成
    target_url = None
    if args.url:
        target_url = args.url
    elif args.grade and args.subject:
        # 根据年级和科目生成URL
        subject_code = subject_map[args.subject]
        target_url = f'https://www.shijuan1.com/a/sj{subject_code}{args.grade}/'
        print(f"根据年级和科目生成URL: {target_url}")
    else:
        print("错误: 必须提供--url参数，或者同时提供--grade和--subject参数")
        return
    
    # 处理输出文件名
    if args.output:
        output_file = args.output
    elif args.grade and args.subject:
        # 根据年级和科目生成输出文件名
        output_file = f'grade{args.grade}_{args.subject}.md'
    else:
        # 使用默认文件名
        output_file = 'papers.md'
    
    # 设置输出路径到pages目录
    pages_dir = Path('/Users/forrest/code/github/data4cici/pages')
    output_path = pages_dir / output_file
    
    print(f"开始爬取试卷信息...")
    print(f"目标网站: {target_url}")
    
    papers = extract_all_papers(target_url)
    if not papers:
        print("未找到任何试卷信息")
        return
    
    save_to_markdown(papers, output_path)


if __name__ == "__main__":
    main()