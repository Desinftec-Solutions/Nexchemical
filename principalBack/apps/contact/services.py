from .models import CompanyInfo, ContactMessage, RegionalOffice


def get_company_info():
    return CompanyInfo.objects.first()


def list_regional_offices():
    return RegionalOffice.objects.all()


def create_contact_message(*, full_name, email, phone_number, message):
    return ContactMessage.objects.create(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        message=message,
    )
