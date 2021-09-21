from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin


class ListRetrieveViewSet(
    ListModelMixin, viewsets.GenericViewSet, RetrieveModelMixin
):
    pass
