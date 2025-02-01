import scrapy


class VntuSpider(scrapy.Spider):
    name = "vntu_test_spider"
    allowed_domains = ["vntu.edu.ua"]
    start_urls = ["https://olimp.vntu.edu.ua/uk/icpc/"]

    def parse(self, response):
        # Заголовок сторінки (тег <h1> з класом `page-title-name`)
        page_title = response.css('h1.page-title-name::text').get()

        # Увесь текст контенту сторінки у блоці `entry-content` (абзаци <p>)
        paragraphs = response.css('div.entry-content p::text').getall()

        # Всі посилання у контенті (теги <a>)
        links = response.css('div.entry-content a::attr(href)').getall()

        # Контактна інформація (regex для телефонів, факсів і email-ів)
        contacts = response.css('div.entry-content').re(r'(Тел\..+|Факс:.+|Email:.+|E-mail:.+)')

        # Зібрана інформація
        yield {
            'page_title': page_title,  # Заголовок сторінки
            'paragraphs': paragraphs,  # Увесь основний текст
            'links': links,  # Усі посилання сторінки
            'contact_information': contacts  # Контакти
        }
