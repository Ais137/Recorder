# Name: UrlExtractor 测试模块
# Date: 2023-10-13
# Author: Ais
# Desc: None


import unittest
from url_extractor import UrlExtractor


class TestUrlExtractor(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        # 构建测试对象
        self.extractor = UrlExtractor()

    def test_extract_url_from_html(self):
        text = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <ul id="article">
                <li><a href="https://www.test.org/article/1"></a></li>
                <li><a href="https://www.test.org/article/2"></a></li>
                <li><a href="https://www.test.org/article/3"></a></li>
                <li><a href="https://www.test.org/article/4"></a></li>
                <li><a href="https://www.test.org/article/5"></a></li>
            </ul>
        </body>
        </html>
        """
        self.assertListEqual(
            self.extractor.extract(
                text = text,
                url_extract_exps = (
                    ("xpath", "//ul[@id='article']/li/a/@href"), 
                )
            ),
            ['https://www.test.org/article/1', 'https://www.test.org/article/2', 'https://www.test.org/article/3', 'https://www.test.org/article/4', 'https://www.test.org/article/5']
        )

    def test_extract_url_from_json(self):
        text = """
        {
            "page_num": 1,
            "page_size": 5,
            "isEnd": false,
            "article": [
                {
                    "title": "test-article-1",
                    "url": "https://www.test.org/article/1"
                },
                {
                    "title": "test-article-2",
                    "url": "https://www.test.org/article/2"
                },
                {
                    "title": "test-article-3",
                    "url": "https://www.test.org/article/3"
                },
                {
                    "title": "test-article-4",
                    "url": "https://www.test.org/article/4"
                },
                {
                    "title": "test-article-5",
                    "url": "https://www.test.org/article/5"
                }
            ] 
        }
        """
        self.assertListEqual(
            self.extractor.extract(
                text = text,
                url_extract_exps = (
                    ("jpath", "/article/\d+/url"),  
                )
            ),
            ['https://www.test.org/article/1', 'https://www.test.org/article/2', 'https://www.test.org/article/3', 'https://www.test.org/article/4', 'https://www.test.org/article/5']
        )

    def test_extract_url_from_html_mixin_json(self):
        text = """
        {
            "page_num": 1,
            "page_size": 5,
            "isEnd": false,
            "article": [
                {
                    "title": "test-article-1",
                    "html": "<div class='article'><h3>test-article-1</h3><a href='https://www.test.org/article/1'></a></div>"
                },
                {
                    "title": "test-article-2",
                    "html": "<div class='article'><h3>test-article-2</h3><a href='https://www.test.org/article/2'></a></div>"
                },
                {
                    "title": "test-article-3",
                    "html": "<div class='article'><h3>test-article-3</h3><a href='https://www.test.org/article/3'></a></div>"
                },
                {
                    "title": "test-article-4",
                    "html": "<div class='article'><h3>test-article-4</h3><a href='https://www.test.org/article/4'></a></div>"
                },
                {
                    "title": "test-article-5",
                    "html": "<div class='article'><h3>test-article-5</h3><a href='https://www.test.org/article/5'></a></div>"
                }
            ] 
        }
        """
        self.assertListEqual(
            self.extractor.extract(
                text = text,
                url_extract_exps = (
                    ("jpath", "/article/\d+/html"), 
                    ("xpath", "//div[@class='article']/a/@href") 
                )
            ),
            ['https://www.test.org/article/1', 'https://www.test.org/article/2', 'https://www.test.org/article/3', 'https://www.test.org/article/4', 'https://www.test.org/article/5']
        )

    def test_extract_url_from_json_mixin_html(self):
        text = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <div class="article" data='{"title": "test-article-1", "url": "https://www.test.org/article/1"}'></div>
            <div class="article" data='{"title": "test-article-2", "url": "https://www.test.org/article/2"}'></div>
            <div class="article" data='{"title": "test-article-3", "url": "https://www.test.org/article/3"}'></div>
            <div class="article" data='{"title": "test-article-4", "url": "https://www.test.org/article/4"}'></div>
            <div class="article" data='{"title": "test-article-5", "url": "https://www.test.org/article/5"}'></div>
        </body>
        </html>
        """
        self.assertListEqual(
            self.extractor.extract(
                text = text,
                url_extract_exps = (
                    ("xpath", "//div[@class='article']/@data"), 
                    ("jpath", "/\d+/url") 
                )
            ),
            ['https://www.test.org/article/1', 'https://www.test.org/article/2', 'https://www.test.org/article/3', 'https://www.test.org/article/4', 'https://www.test.org/article/5']
        )
        text = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <title>News</title>
            <script>
                data={"page_num": 1, "page_size": 5,"isEnd":false, "article": [{"title": "test-article-1","url": "https://www.test.org/article/1"},{"title": "test-article-2","url": "https://www.test.org/article/2"},{"title": "test-article-3","url": "https://www.test.org/article/3"},{"title": "test-article-4","url": "https://www.test.org/article/4"},{"title":"test-article-5", "url":"https://www.test.org/article/5"}]}
            </script>
        </body>
        </html>
        """
        self.assertListEqual(
            self.extractor.extract(
                text = text,
                url_extract_exps = (
                    ("regex", "data=(.+?)\n", {"toStr": True}), 
                    ("jpath", "/article/\d+/url")
                )
            ),
            ['https://www.test.org/article/1', 'https://www.test.org/article/2', 'https://www.test.org/article/3', 'https://www.test.org/article/4', 'https://www.test.org/article/5']
        )
    


if __name__ ==  "__main__":
    
    unittest.main()