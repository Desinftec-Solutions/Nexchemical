from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from . import services
from .models import NewsArticle

NEWS_PER_PAGE = 9


def news_list(request):
    articles = services.list_published_news()

    paginator = Paginator(articles, NEWS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "articles": page_obj,
        "page_obj": page_obj,
        "elided_page_range": paginator.get_elided_page_range(
            page_obj.number, on_each_side=1, on_ends=1
        ),
    }
    return render(request, "news/news_list.html", context)


def news_detail(request, slug):
    try:
        article = services.get_published_news(slug)
    except NewsArticle.DoesNotExist:
        raise Http404("News article not found")

    return render(request, "news/news_detail.html", {"article": article})
