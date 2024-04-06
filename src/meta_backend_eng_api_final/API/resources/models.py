"""
Module: resources.models

This module contains the definition of various models related to a restaurant ordering system.

The models included are:
- Category: Represents a category of menu items.
- MenuItem: Represents a menu item available for order.
- Order: Represents an order placed by a user.
- OrderItem: Represents an item within an order.
- Cart: Represents a user's shopping cart.

Each model inherits from the SoftDeleteObject class, allowing for soft deletion of records.

The module also includes methods for handling operations related to the models, such as resetting a user's cart in the Cart model.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta
from loguru import logger
from softdelete.models import SoftDeleteObject


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return str(self.title)

    class Meta(TypedModelMeta):
        db_table = "category"
        order_with_respect_to = "title"
        verbose_name = "category"
        verbose_name_plural = "categories"


class MenuItem(SoftDeleteObject, models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return str(self.title)

    class Meta(TypedModelMeta):
        db_table = "menu_items"
        order_with_respect_to = "title"
        verbose_name = "menu item"
        verbose_name_plural = "menu items"


class Order(SoftDeleteObject, models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
        blank=True,
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True, auto_created=True)

    def __str__(self) -> str:
        return f"Order Number: {self.pk} - {self.user.last_name}, {self.user.last_name}"

    class Meta(TypedModelMeta):
        db_table = "orders"
        ordering = ["-date"]
        get_latest_by = "date"
        verbose_name = "order"
        verbose_name_plural = "orders"


class OrderItem(SoftDeleteObject, models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)

    def __str__(self) -> str:
        return str(self.title)

    class Meta(TypedModelMeta):
        db_table = "order_items"
        order_with_respect_to = "order"
        verbose_name = "order item"
        verbose_name_plural = "order items"
        unique_together = ("menuitem", "order")


class Cart(SoftDeleteObject, models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)

    def __str__(self) -> str:
        return f"Cart for '{self.user.last_name}, {self.user.last_name}"

    def reset_cart(self) -> None:
        """
        `        Soft deletes the user's cart.

                This method soft deletes the user's cart by setting the 'deleted' flag to True.
                The cart is not permanently removed from the database, allowing for potential recovery of the cart data.

                Args:
                    None

                Raises:
                    Exception: If an error occurs during the soft deletion process.

                Returns:
                    None
        """
        try:
            logger.warning(
                f"Soft-Deleteting {self.user.last_name}, {self.user.last_name}({self.id}) cart"
            )
            self.delete()
        except Exception as e:
            logger.error("Error deleting cart", exc_info=e)

    # TODO: Implement Logic to 1. Convert the Current Contents of an  Order Object , 2. After Creation, Empty (Delete Possibily the contents of the cart)
    def checkout(self):
        raise NotImplementedError

    class Meta(TypedModelMeta):
        db_table = "user_carts"
        order_with_respect_to = "user"
        verbose_name = "cart"
        verbose_name_plural = "carts"
        unique_together = ("menuitem", "user")
