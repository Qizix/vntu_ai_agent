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

        # Витяг тексту з використанням загальних селекторів
        raw_text = self.extract_clean_text(response)

        # Аналіз сторінки на корисність
        if self.is_page_not_useful(raw_text, response):
            self.logger.warning(f"Сторінка '{response.url}' мала некорисний контент. Пропущено.")
            return  # Пропускаємо некорисні сторінки

        # Отримання всіх посилань сторінки
        all_links = response.css("a::attr(href)").getall()
        all_links = self.filter_links(response, all_links)

        self.logger.debug(f"На сторінці знайдено загалом {len(all_links)} посилань.")

        # Збереження результатів
        yield {
            "url": response.url,
            "cleaned_main_text": raw_text,  # Основний текст сторінки
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

    def is_page_not_useful(self, text, response):
        """
            Аналіз сторінки, щоб виявити некорисний контент.
            """
        # 1. Якщо сторінка не містить тексту:
        if not text or len(text.strip()) == 0:
            self.logger.info(f"Сторінка '{response.url}' містить порожній текст.")
            return True

        # 2. Якщо текст занадто короткий:
        if len(text) < 100:  # Мінімальна кількість символів для визнання сторінки корисною
            self.logger.info(f"Сторінка '{response.url}' має дуже короткий текст ({len(text)} символів).")
            return True

        # 3. Якщо в тексті містяться загальні службові терміни:
        useless_keywords = [
            "404", "сторінка не знайдена", "завантаження", "доступ заборонено",  # Помилки
            "авторські права", "політика конфіденційності", "публічна оферта",  # Службові
            "архів", "старий контент", "звіт", "переглянути статистику",  # Архіви та звіти
            "всі права захищені", "університет залишає за собою право"  # Типові службові тексти
        ]
        if any(keyword.lower() in text.lower() for keyword in useless_keywords):
            self.logger.info(f"Сторінка '{response.url}' містить службову або некорисну інформацію.")
            return True

        # 4. Додаткові виключення за URL:
        exclude_terms_in_url = [
            "login", "signin", "register", "search",  # Форми входу чи реєстрації
            "policy", "copyright", "terms", "archive",  # Політики, авторські права, архіви
            "admin", "user", "feedback", "contact", "privacy"  # Адмін, контакти, інше
        ]
        if any(term in response.url.lower() for term in exclude_terms_in_url):
            self.logger.info(f"Сторінка '{response.url}' є службовою (за URL).")
            return True

        # Якщо всі умови не виконані - сторінка корисна
        return False

    def filter_links(self, response, links):
        """
        Фільтрація посилань, залишаючи лише ті, що належать wiki.vntu.edu.ua,
        та виключення зображень або інших типів файлів, а також сторінок із "Спеціальна:".
        """
        # Абсолютні посилання
        links = [response.urljoin(link) for link in links]

        # Фільтруємо посилання
        filtered_links = [
            link for link in links
            if ("wiki.vntu.edu.ua" in link and
                not link.endswith((".jpg", ".png", ".pdf", ".JPG", ".gif")) and
                "Спеціальна:" not in link and
                "%D0%A1%D0%BF%D0%B5%D1%86%D1%96%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0:" not in link)
        ]

        return filtered_links