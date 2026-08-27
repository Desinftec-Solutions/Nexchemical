from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    cover_image = models.ImageField(upload_to="news/")
    excerpt = models.CharField(
        max_length=300, blank=True, help_text="Short summary shown on the news card."
    )
    body = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
