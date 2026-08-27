from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from . import services
from .forms import ContactMessageForm


def contact_page(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            services.create_contact_message(**form.cleaned_data)
            messages.success(request, _("Thanks for reaching out — we will get back to you soon."))
            return redirect("contact:contact_page")
    else:
        form = ContactMessageForm()

    context = {
        "form": form,
        "company_info": services.get_company_info(),
        "regional_offices": services.list_regional_offices(),
    }
    return render(request, "contact/contact_page.html", context)
