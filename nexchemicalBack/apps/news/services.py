from .models import NewsArticle


def list_published_news():
    return NewsArticle.objects.filter(is_published=True)


def get_published_news(slug):
    return NewsArticle.objects.get(slug=slug, is_published=True)
