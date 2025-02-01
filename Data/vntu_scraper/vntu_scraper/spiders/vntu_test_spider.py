import scrapy
from urllib.parse import urljoin  # Для створення абсолютних URL
from w3lib.html import remove_tags  # Для очищення HTML-тегів
import re


class VntuSpider(scrapy.Spider):
    name = "vntu_test_spider"
    allowed_domains = ["vntu.edu.ua"]  # Робота тільки в рамках домену
    start_urls = ["https://vstup.vntu.edu.ua/"]  # Початкова сторінка
    visited_links = set()  # Для зберігання унікальних посилань
    counter = 0  # Лічильник оброблених сторінок

    def parse(self, response):
        # Лічильник оброблених сторінок
        self.counter += 1

        # Лог обробки поточної сторінки
        self.logger.info(
            f"[{self.counter}] Обробляється сторінка: {response.url}"
        )
        # Збираємо текст із блоку <main> та очищаємо
        raw_main_text = response.css('main *::text').getall()
        clean_main_text = self.clean_text(" ".join(raw_main_text))

        # Знаходимо й фільтруємо посилання із блоку <main>
        main_links = response.css('main a::attr(href)').getall()
        main_links = self.filter_links(response, main_links)

        # Лог для кількості знайдених посилань
        self.logger.debug(
            f"На сторінці знайдено {len(main_links)} посилань для переходу."
        )

        # Збереження результатів
        yield {
            'url': response.url,
            'cleaned_main_text': clean_main_text,

        }

        # Перехід до інших сторінок (обхід посилань)
        for link in main_links:
            if link not in self.visited_links:
                self.visited_links.add(link)
                self.logger.info(f"Перехід на сторінку: {link}")
                yield scrapy.Request(url=link, callback=self.parse)

    def clean_text(self, text):
        """
        Очищує текст:
        - Видаляє HTML-теги.
        - Забирає зайві перенос рядків, табуляції та множинні пробіли.
        """
        text = remove_tags(text)  # Видалення HTML-тегів
        text = re.sub(r'\s+', ' ', text)  # Усунення повторів пробілів і табуляцій
        return text.strip()  # Видалення пробілів по краях

    def filter_links(self, response, links):
        """
        Фільтрує посилання:
        - Перетворює у абсолютні посилання.
        - Відбирає лише ті, які належать домену vntu.edu.ua.
        """
        links = [response.urljoin(link) for link in links]
        filtered_links = [link for link in links if "vntu.edu.ua" in link]

        return filtered_links