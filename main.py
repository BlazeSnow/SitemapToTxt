import requests
from xml.etree import ElementTree as ET
from urllib.parse import urlparse


def extract_urls(sitemap_url, output_file=None):
    """
    从 sitemap.xml 提取所有 URL
    参数:
        sitemap_url: sitemap.xml 的 URL
        output_file: 保存结果的文件路径（可选）
    """
    try:
        # 设置通用 headers 避免被拦截
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
        }

        # 获取 sitemap 内容
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析 XML
        root = ET.fromstring(response.content)

        # 定义 sitemap 命名空间
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        urls = []

        # 检查是否是 sitemap 索引文件
        if root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex":
            print("发现 sitemap 索引文件，开始递归处理...")
            # 提取所有子 sitemap 链接
            for sitemap in root.findall("sm:sitemap", namespace):
                loc = sitemap.find("sm:loc", namespace).text.strip()
                print(f"正在处理子 sitemap: {loc}")
                urls += extract_urls(loc)

        # 如果是普通 sitemap
        elif root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
            for url in root.findall("sm:url", namespace):
                loc = url.find("sm:loc", namespace).text.strip()
                # 基本 URL 有效性验证
                if urlparse(loc).scheme in ("http", "https"):
                    urls.append(loc)
                    print(f"Found URL: {loc}")
                else:
                    print(f"忽略无效 URL: {loc}")

        # 保存结果到文件
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(urls))
            print(f"\n已保存 {len(urls)} 个链接到 {output_file}")

        return list(set(urls))  # 去重后返回

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return []


# 使用示例
if __name__ == "__main__":
    sitemap_url = "https://blazesnow.com/sitemap.xml"  # 替换为你的sitemap地址
    output_path = "urls.txt"  # 输出文件路径

    all_urls = extract_urls(sitemap_url, output_path)

    print("\n总计提取链接数量:", len(all_urls))
    print("前5个链接示例:")
    for url in all_urls[:5]:
        print(url)
