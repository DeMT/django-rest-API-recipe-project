from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from app.models import Tag, Ingredient, Recipe

from .import serializers


class BaseUserOnlyViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """Base class for user only behavior that related to recipes contents"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user)  \
            .order_by('name')   \
            .distinct()

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


class RecipeViewSet(viewsets.ModelViewSet):
    """ Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, string):
        """Convert a string of object IDs to a list of integers."""
        return [int(str_id) for str_id in string.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for authenticated user"""
        queryset = self.queryset.filter(user=self.request.user).order_by('id')
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        if self.action == 'upload_image':
            return queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        queryset = self.get_serializer_class()             \
            .setup_eager_loading(queryset=queryset)
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializers):
        """Create a new recipe"""
        serializers.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )
