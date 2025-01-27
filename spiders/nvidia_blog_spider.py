import scrapy

class NvidiaBlogSpider(scrapy.Spider):
    name = "nvidia_blog"
    allowed_domains = ["blogs.nvidia.com"]
    start_urls = [
        "https://blogs.nvidia.com/blog/category/generative-ai/"
    ]

    def parse(self, response):
        """
        Faz o parsing dos posts na página principal da categoria “Generative AI”
        """
        posts = response.css("article.excerpt")  # cada artigo listado
        for post in posts:
            title_el = post.css(".entry-title a")
            title = title_el.css("::text").get() or ""
            link = title_el.css("::attr(href)").get() or ""

            # A “excerpt” ou “resumo” geralmente está dentro de
            # .article-excerpt ou .entry-excerpt . 
            # Vamos tentar extrair o texto principal do snippet:
            excerpt_el = post.css(".article-excerpt p") or post.css(".entry-excerpt p")
            excerpt = excerpt_el.getall()
            # Ou se quisermos texto puro, algo como:
            excerpt_text = " ".join(
                [p.strip() for p in excerpt_el.css("::text").getall()]
            )

            yield {
                "title": title.strip(),
                "link": link.strip(),
                "content": excerpt_text.strip()
            }

        # Se a página tiver paginação (no caso do “Load More Articles”),
        # normalmente é um botão que faz requisição AJAX, sem link tradicional.
        # Para Scrapy, extrair links de "next page" seria algo como:
        # next_page = response.css(".load-more-wrapper button::attr(data-page-id)").get()
        # ... mas esse site carrega dinamicamente via JavaScript.
        # Se quiser extrair mais do que a 1ª página, é preciso
        # ou simular AJAX ou usar Selenium/Playwright com Scrapy.
        #
        # Por ora, sem suporte a 'load more' dinâmico, paramos aqui.
