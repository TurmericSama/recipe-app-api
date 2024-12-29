"""
URL mappings for recipe app
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

# from drf_spectacular.views import (
#     SpectacularAPIView,
#     SpectacularSwaggerView,
# )

router = DefaultRouter()
router.register("recipes", views.RecipeViewSet)

app_name = "recipe"

urlpatterns = [
    path("", include(router.urls)),
    # path("api/schema", SpectacularAPIView.as_view(), name="api-schema"),
    # path(
    #     "api/docs",
    #     SpectacularSwaggerView.as_view(url_name="api-schema"),
    #     name="api-docs",
    # ),
    # path("api/user", include("user.urls")),
    # path("api/recipe", include("recipe.urls")),
]
