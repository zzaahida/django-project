from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Product


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'phone', 'last_name', 'first_name', 'money']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'image', 'selling_price', 'marked_price', 'description', 'created_at', 'count']
