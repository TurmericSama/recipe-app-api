"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta: 
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagDetailSerializer(TagSerializer):
    """Serializer for tag detail view"""

    class Meta(TagSerializer.Meta):
        fields = TagSerializer.Meta.fields + ['user']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", 'tags', 'ingredients']
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed"""
        auth_user = self.context['request'].user
        for ingredients in ingredients:
            ing_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredients
            )
            recipe.ingredients.add(ing_obj)
        
    def create(self, validated_data):
        """Create a recipe"""
        # take tags object from validated data and assign to variable tags
        # if tags is not present, assign an empty list to tags
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # create a new recipe object with the validated data
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe
    
    # update method is required when we want to update a nested serializer
    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if(tags is not None):
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        
        if(ingredients is not None):
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]

