import scrapy
from urllib.parse import urljoin
from w3lib.html import remove_tags
import re


class VntuSpider(scrapy.Spider):
    name = "vntu_wiki_spider"
    allowed_domains = ["wiki.vntu.edu.ua"]
    start_urls = ["https://wiki.vntu.edu.ua/"]
    visited_links = set()
    counter = 0

    def parse(self, response):

        self.counter += 1
        self.logger.info(f"[{self.counter}] Обробляється сторінка: {response.url}")

        # Вибір тексту тільки з div.content
        raw_text, main_links_inside_div = self.extract_clean_text(response)

        # Отримання всіх посилань сторінки (включаючи поза div.content)
        all_links = response.css("a::attr(href)").getall()
        all_links = self.filter_links(response, all_links)

        self.logger.debug(f"На сторінці знайдено загалом {len(all_links)} посилань.")

        # Збереження результатів
        yield {
            "url": response.url,
            "cleaned_main_text": raw_text,  # Текст тільки з div.content
        }

        # Перехід до інших сторінок
        for link in all_links:
            if link not in self.visited_links:
                self.visited_links.add(link)
                self.logger.info(f"Перехід на сторінку: {link}")
                yield scrapy.Request(url=link, callback=self.parse)

    def extract_clean_text(self, response):
        """
        Вибірка тексту з div.content + витягання внутрішніх посилань.
        """
        # Витягуємо тільки текст з div.content
        elements = response.css("div#content *::text").getall()
        if elements:
            text = self.clean_text(" ".join(elements))
            links_inside_div = response.css("div#content a::attr(href)").getall()  # Посилання в div.content
            return text, links_inside_div

        return "", []  # Якщо контент не знайдено

    def clean_text(self, text):
        """
        Очищення тексту: видалення HTML-тегів, зайвих пробілів, скриптів тощо.
        """
        text = remove_tags(text)
        text = re.sub(r"\s+", " ", text)  # Усунення повторів пробілів
        text = re.sub(r"\|", " ", text)  # Видалення зайвих вертикальних рисок
        text = re.sub(r"\b(подробиці|читати далі)\b", "", text, flags=re.I)  # Видалення зайвих фраз
        return text.strip()

    def filter_links(self, response, links):
        """
        Фільтрація посилань, залишаючи лише ті, що належать wiki.vntu.edu.ua,
        та виключення зображень або інших типів файлів.
        """
        # Абсолютні посилання
        links = [response.urljoin(link) for link in links]
        # Фільтруємо посилання
        return [link for link in links if ("wiki.vntu.edu.ua" in link and not link.endswith((".jpg", ".png", ".pdf", ".JPG", ".gif")))]
