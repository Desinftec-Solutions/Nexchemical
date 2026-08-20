from django.urls import path

from . import api_views

urlpatterns = [
    path("messages/", api_views.ContactMessageCreateView.as_view(), name="contact-message-create"),
    path("company-info/", api_views.CompanyInfoView.as_view(), name="company-info"),
    path("offices/", api_views.RegionalOfficeListView.as_view(), name="regional-office-list"),
]
