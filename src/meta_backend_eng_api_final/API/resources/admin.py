from django.contrib import admin
from resources.models import Cart, Category, Order, OrderItem, get_user_model

# Register your models here.

for model in [Cart, Category, Order, OrderItem, get_user_model()]:
    admin.register(model)
