from django.db import models
from django.utils.text import slugify
from django.conf import settings


#################### CASH-ON-DELIVERY #######################

import uuid

############# EMAIL OTP ######################

from django.utils import timezone
from datetime import timedelta

##########################################

class Product(models.Model):
    CATEGORY_CHOICES = [
        # Main Categories
        ('ABSTRACT', 'Abstract Art'),
        ('SCULPTURE', 'Sculpture'),
        ('PORTRAIT', 'Portrait Paintings'),
        ('LANDSCAPE', 'Landscape Paintings'),
        ('DIGITAL', 'Digital Art'),
        ('SUPPLIES', 'Painting Supplies'),
        ('DECAL', 'Wall Decals'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in cart {self.cart.id}'

class Order(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True
    )
    order_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    order_note = models.TextField(blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='Pending'
    )
    ip = models.CharField(max_length=50, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


##########################################
 #(cod)

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for order {self.order.order_number}"


################ EMAIL OTP ####################

class EmailVerification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Email verification for {self.user.email}"
    

########################### DASHBOARD ###################################

class Country(models.Model): 
    name = models.CharField(max_length=200)

class Gender(models.Model): 
    name = models.CharField(max_length=200)

class CustomerType(models.Model): 
    name = models.CharField(max_length=200)

class StoreSales(models.Model): 
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    customertype = models.ForeignKey(CustomerType, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
