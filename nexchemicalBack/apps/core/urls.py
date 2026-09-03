from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    # Service page is hidden pending accurate service copy (see PR #14) —
    # its content still asserts agriculture-specific capabilities the
    # business doesn't have. Re-add once that copy is settled.
    # path("service/", views.service, name="service"),
]
