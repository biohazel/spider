import scrapy
from datetime import datetime, timedelta

class NvidiaBlogSpider(scrapy.Spider):
    name = "nvidia_blog"
    allowed_domains = ["blogs.nvidia.com"]

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            # URL default, se não for passada via -a url=...
            self.start_urls = ["https://blogs.nvidia.com/blog/category/generative-ai/"]
        
        # Se quiser filtrar só HOJE e ONTEM
        self.hoje = datetime.now().date()
        self.ontem = (datetime.now() - timedelta(days=1)).date()

    def parse(self, response):
        """
        1) Captura artigos listados na página (cada "article.excerpt").
        2) Para cada, extrai título/link/excerpt e chama parse_post para pegar data
        """
        posts = response.css("article.excerpt")
        if not posts:
            self.logger.info("Nenhum artigo foi encontrado com 'article.excerpt'.")

        for post in posts:
            title_el = post.css(".entry-title a")
            title = title_el.css("::text").get() or ""
            link = title_el.css("::attr(href)").get() or ""

            # A excerpt/summary
            excerpt_el = post.css(".article-excerpt p") or post.css(".entry-excerpt p")
            excerpt_text = " ".join(
                [p.strip() for p in excerpt_el.css("::text").getall()]
            )

            # Faz request para a página do post individual, onde extrairemos a data
            yield scrapy.Request(
                url=link,
                callback=self.parse_post,
                meta={
                    "title": title.strip(),
                    "link": link.strip(),
                    "content": excerpt_text.strip()
                }
            )
        
        # Observação: o "Load More" do blog da NVIDIA é via AJAX/JS, 
        # então a spider padrão não seguirá automaticamente. 
        # Se houvesse paginação em links "next", faríamos algo aqui.
        # next_page = response.css("a.next::attr(href)").get()
        # if next_page: yield scrapy.Request(next_page, callback=self.parse)

    def parse_post(self, response):
        """
        Extrai data de publicação do post e filtra artigos
        que sejam de hoje ou ontem.
        """
        title = response.meta["title"]
        link = response.meta["link"]
        content = response.meta["content"]

        # Tenta extrair data no <time entry-date>, ex.: <time class="entry-date" datetime="2025-03-15T08:00:00">
        date_str = response.css("time.entry-date::attr(datetime)").get()
        if not date_str:
            # fallback: meta tag article:published_time
            date_str = response.css("meta[property='article:published_time']::attr(content)").get()

        if not date_str:
            self.logger.warning(f"Não foi possível obter data para {link}. Ignorando...")
            return

        published_dt = None
        try:
            # Se for ISO, ex. "2025-03-14T10:22:00"
            published_dt = datetime.fromisoformat(date_str.strip())
        except ValueError:
            # Se vier formato diferente, tente outro .strptime
            try:
                # Ex.: "Mar 14, 2025"
                published_dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
            except:
                self.logger.warning(f"Falha ao converter data={date_str} no link={link}")
                return
        
        # Filtro: HOJE ou ONTEM
        data_artigo = published_dt.date()
        if data_artigo == self.hoje or data_artigo == self.ontem:
            yield {
                "title": title,
                "link": link,
                "content": content,
                "publishedAt": published_dt.isoformat(),  # formata p/ ISO8601
                "source": "scraping"
            }
        else:
            self.logger.info(f"Ignorando artigo '{title}' (data {published_dt.isoformat()} não é hoje/ontem).")
