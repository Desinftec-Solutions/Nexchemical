from . import services


def company_info(request):
    """Makes company_info (phone/email/address/map) available in every template, e.g. the footer."""
    return {"company_info": services.get_company_info()}
