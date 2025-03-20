import scrapy
from urllib.parse import urljoin
from w3lib.html import remove_tags
import re


class VntuSpider(scrapy.Spider):
    name = "vntu_spider"
    allowed_domains = ["vntu.edu.ua"]
    start_urls = ["https://vntu.edu.ua/uk/about-university/vntu-today.html"]
    visited_links = set()
    counter = 0

    TEXT_SELECTORS = [
        "div#content",
        "div.content",
        "article",
        "section",
        "main",  # Основна частина сторінки
    ]

    def parse(self, response):

        self.counter += 1
        self.logger.info(f"[{self.counter}] Обробляється сторінка: {response.url}")

        raw_text = self.extract_clean_text(response)

        all_links = response.css("a::attr(href)").getall()
        all_links = self.filter_links(response, all_links)

        self.logger.debug(f"На сторінці знайдено загалом {len(all_links)} посилань.")

        yield {
            "url": response.url,
            "cleaned_main_text": raw_text,
        }


        for link in all_links:
            if link not in self.visited_links:
                self.visited_links.add(link)
                self.logger.info(f"Перехід на сторінку: {link}")
                yield scrapy.Request(url=link, callback=self.parse)

    def extract_clean_text(self, response, custom_selectors=None):

        selectors = custom_selectors or self.TEXT_SELECTORS
        for sel in selectors:
            elements = response.css(f"{sel} *::text").getall()
            if elements:
                text = self.clean_text(" ".join(elements))
                if text:
                    self.logger.info(f"Текст знайдено за селектором: {sel}")
                    return text

        self.logger.warning(f"Не вдалося знайти текст за жодним із селекторів на сторінці: {response.url}")
        return ""

    def clean_text(self, text):
        text = remove_tags(text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\|", " ", text)
        text = re.sub(r"\b(подробиці|читати далі|деталі)\b", "", text, flags=re.I)
        return text.strip()

    def filter_links(self, response, links):

        links = [response.urljoin(link) for link in links]


        filtered_links = [
            link for link in links
            if ("vntu.edu.ua" in link and
                not link.endswith((".jpg", ".pdf", ".JPG", ".gif")) and
                "Спеціальна:" not in link and
                "%D0%A1%D0%BF%D0%B5%D1%86%D1%96%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0:" not in link and
                "ir.lib" not in link and
                "conferences" not in link and
                "pedbezpeka" not in link and
                "visnyk" not in link and
                "repository" not in link and
                "method" not in link and
                "praci" not in link and
                "vmt" not in link
                )
        ]

        return filtered_links
