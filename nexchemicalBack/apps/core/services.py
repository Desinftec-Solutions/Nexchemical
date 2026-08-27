from .models import Certificate, Partner


def list_certificates():
    return Certificate.objects.all()


def list_partners():
    return Partner.objects.all()
