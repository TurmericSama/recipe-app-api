"""
Test for ingredients API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """Create and return an ingredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id]) 


def create_user(email="user@example.com", password="password"):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)

class PublicIngredientsApiTest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is requred for retrieving ingredients"""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientApiTest(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user) #force authentication to simulate an authenticated user

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        res = self.client.get(INGREDIENTS_URL)


        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

        names = [ingredient['name'] for ingredient in res.data] # extract the names from the response data
        self.assertIn("Kale", names)
        self.assertIn("Vanilla", names)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""
        user2 = create_user(email="user2@mail.com") # remember that you already have a user created in the setup method
        Ingredient.objects.create(user=user2, name="Salt")
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        # this new instance of Ingredient model does not have any context of other instances of Ingredient model
        # this is a blank slate, we are only expecting ingredient to be created in the database
        ingredient = Ingredient.objects.create(user=self.user, name="Cilantro")
        payload = {
            'name': 'Coriander',
        }
        url = detail_url(ingredient.id) # create a detail url from the id of the newly created ingredient
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK) # check if the status code is 200
        ingredient.refresh_from_db() # refetch items from db
        self.assertEqual(ingredient.name, payload['name']) # check if the name of the ingredient is equal to the name in the payload

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name="Paprika")
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
        # NOTE: Don't call refresh_from_db() on previous objects after deleting them coz the don't exist, it will be an error
