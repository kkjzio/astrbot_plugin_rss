import os
import json
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import re

class DataHandler:
    def __init__(self, config_path="data/astrbot_plugin_rss_data.json", default_config=None):
        self.config_path = config_path
        self.default_config = default_config or {
            "rsshub_endpoints": []
        }
        self.data = self.load_data()

    def get_subs_channel_url(self, user_id) -> list:
        """获取用户订阅的频道 url 列表"""
        subs_url = []
        for url, info in self.data.items():
            if url == "rsshub_endpoints" or url == "settings":
                continue
            if user_id in info["subscribers"]:
                subs_url.append(url)
        return subs_url

    def load_data(self):
        """从数据文件中加载数据"""
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(self.default_config, indent=2, ensure_ascii=False))
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self):
        """保存数据到数据文件"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def parse_channel_info(self, text):
        """解析RSS频道信息"""
        root = etree.fromstring(text)
        title = root.xpath("//title")[0].text
        description = root.xpath("//description")[0].text
        return title, description


    # def _process_element(self, element, ordered_content):
    #     """递归处理HTML元素，保持内容顺序"""
    #     # 处理文本节点
    #     if element.name is None and element.string and element.string.strip():
    #         text = element.string.strip()
    #         if text:
    #             ordered_content.append({"type": "text", "content": text})
    #     # 处理图片节点
    #     elif element.name == 'img':
    #         img_src = element.get('src')
    #         if img_src:
    #             ordered_content.append({"type": "image", "content": img_src})
    #     # 递归处理子节点
    #     for child in element.children:
    #         if isinstance(child, str):
    #             # 跳过特殊字符串节点
    #             continue
    #         self._process_element(child, ordered_content)

    def strip_html_pic(self, html)-> list[str]:
        """解析HTML内容，提取图片地址
        """
        soup = BeautifulSoup(html, "html.parser")
        ordered_content = []

        # 处理图片节点
        for img in soup.find_all('img'):
            img_src = img.get('src')
            if img_src:
                ordered_content.append(img_src)

        return ordered_content

    # def get_limited_comps_text(self, comps, limit=1000):
    #     """限制文本长度,处理列表中type为text的元素，保证所有的text字符全部加起来最大值不超过限制值,并保留在限制值之前的图片"""
    #     total_length = 0
    #     limited_comps = []
    #     for comp in comps:
    #         if comp["type"] == "text":
    #             text = comp["content"]
    #             text_length = len(text)
    #             if total_length + text_length > limit:
    #                 # 超过限制，截断文本
    #                 text = text[:limit - total_length]
    #                 # total_length += len(text)
    #                 limited_comps.append({"type": "text", "content": text + "..."})
    #                 break
    #             else:
    #                 total_length += text_length
    #         limited_comps.append(comp)
    #     return limited_comps

    def strip_html(self, html):
        """去除HTML标签"""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        return re.sub(r"\n+", "\n", text)

    def get_root_url(self, url):
        """获取URL的根域名"""
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
