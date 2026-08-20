from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import CompanyInfoSerializer, ContactMessageSerializer, RegionalOfficeSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer

    def perform_create(self, serializer):
        services.create_contact_message(**serializer.validated_data)


class CompanyInfoView(APIView):
    def get(self, request):
        info = services.get_company_info()
        if info is None:
            return Response({})
        return Response(CompanyInfoSerializer(info).data)


class RegionalOfficeListView(generics.ListAPIView):
    serializer_class = RegionalOfficeSerializer

    def get_queryset(self):
        return services.list_regional_offices()
