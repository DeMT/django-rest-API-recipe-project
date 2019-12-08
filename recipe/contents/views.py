from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from app.models import Tag, Ingredient

from .import serializers


class BaseUserOnlyViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """Base class for user only behavior that related to recipes contents"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        """Create a new model object for authenticated user"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseUserOnlyViewSet):
    """Mange tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseUserOnlyViewSet):
    """ Manage ingredients in the database."""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """ Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)
