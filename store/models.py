# store/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. Will be auto-populated from email if left blank during registration.'),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        null=True,
        blank=True
    )
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('Full name'), max_length=255, blank=True, help_text=_('Full name of the user.'))

    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='customer',
        help_text=_('User role in the system.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) # Added description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) # Added stock

    def __str__(self):
        return self.name

class Basket(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),       # Customer is currently building this basket
        ('submitted', 'Submitted'), # Customer has submitted for processing by staff
        ('approved', 'Approved'),   # Staff has approved the basket/order
        ('denied', 'Denied'),       # Staff has denied the basket/order
        ('abandoned', 'Abandoned'), # Customer left it active for too long (future use)
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='baskets')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket {self.id} for {self.user.email} ({self.get_status_display()})"
    @property
    def total_price(self):
        # Ensure items and their products are efficiently fetched if not already
        # This might be better done in the view with prefetch_related
        return sum(item.total_price for item in self.items.all())

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('basket', 'product') # A product can only be in a basket once per item row

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Basket {self.basket.id}"

    @property
    def total_price(self):
        return self.product.price * self.quantity
