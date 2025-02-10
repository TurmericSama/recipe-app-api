"""
Tests for tags api
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase 


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list') # /api/recipe/tags/ get the array of tags endpoint

def detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)

class PublicTagsApiTests(TestCase):
    """Test auth is required for retrieving tags."""
    # setup is a method that runs before every test, remember to define it 
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user) # type: ignore
    
    def test_retrieve_tags(self):
        """Test retrieve a list of tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_current_user(self):
        """Test list of tags is limited to current authenticated user"""
        # create a second user
        user2 = create_user(email="user2@example.com", password="testpass123")
        # create a tag for second user we just created
        Tag.objects.create(user=user2, name="Fruity")
        # create a tag for the authenticated/current user
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        # get the tags for the authenticated user
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check if the length of the data is 1 for the authenticated user
        self.assertEqual(len(res.data), 1)
        # check if the name of the tag is equal to the name of the tag we created for the authenticated user
        self.assertEqual(res.data[0]['name'], tag.name)
        # check if the id of the tag is equal to the id of the tag we created for the authenticated user
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name="After Dinner")
        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # refresh data from db after doing the patch
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test Deleting a tag is successful"""

        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        # delete the tag
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        # check that the tag does not exist
        self.assertFalse(tags.exists())