import scrapy
from urllib.parse import urljoin  # Для створення абсолютних URL
from w3lib.html import remove_tags  # Для очищення HTML-тегів
import re


class VntuSpider(scrapy.Spider):
    name = "vntu_test_spider"
    allowed_domains = ["vntu.edu.ua"]  # Робота тільки в рамках домену
    start_urls = ["https://vstup.vntu.edu.ua/"]  # Початкова сторінка
    visited_links = set()  # Для зберігання унікальних посилань

    def parse(self, response):
        # Очищення тексту в <main>
        raw_main_text = response.css('main *::text').getall()  # Весь текст із блоку <main>
        clean_main_text = self.clean_text(" ".join(raw_main_text))  # Очищення тексту

        # Знаходимо всі посилання в <main> і фільтруємо тільки коректні
        main_links = response.css('main a::attr(href)').getall()
        main_links = self.filter_links(response, main_links)

        # Збереження очищених даних
        yield {
            'url': response.url,  # URL поточної сторінки
            'cleaned_main_text': clean_main_text,  # Очищений текст із <main>
        }

        # Переходимо на кожне унікальне посилання
        for link in main_links:
            if link not in self.visited_links:
                self.visited_links.add(link)
                yield scrapy.Request(url=link, callback=self.parse)

    def clean_text(self, text):
        """
        Очищує текст:
        - Забирає зайві символи \n, \t.
        - Видаляє HTML-теги.
        - Позбувається повторів пробілів.
        """
        text = remove_tags(text)  # Видалення HTML-тегів
        text = re.sub(r'\s+', ' ', text)  # Замінюємо множинні пробіли, перенос рядків і табуляцію на один пробіл
        return text.strip()  # Обрізаємо зайві пробіли по краях

    def filter_links(self, response, links):
        """
        Фільтрує посилання:
        - Повертає лише посилання з доменом vntu.edu.ua.
        """
        links = [response.urljoin(link) for link in links]  # Перетворюємо в абсолютні URL
        filtered_links = [link for link in links if "vntu.edu.ua" in link]
        return filtered_links
