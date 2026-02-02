from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SHG(models.Model):
    VERIFICATION_CHOICES = [
        ('bronze', _('Bronze')),
        ('silver', _('Silver')),
        ('gold', _('Gold')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    verification_level = models.CharField(max_length=10, choices=VERIFICATION_CHOICES, default='bronze')
    logo = models.ImageField(upload_to='shg_logos/', blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('live', _('Live')),
        ('rejected', _('Rejected')),
    ]
    
    CATEGORY_CHOICES = [
        ('handicrafts', _('Handicrafts')),
        ('food', _('Food Products')),
        ('textiles', _('Textiles')),
        ('pottery', _('Pottery')),
        ('jewelry', _('Jewelry')),
        ('other', _('Other')),
    ]
    
    shg = models.ForeignKey(SHG, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='product_images/')
    inventory = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    removal_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class LedgerEntry(models.Model):
    shg = models.ForeignKey(SHG, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=200)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.shg.name} - {self.description}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending_admin_approval', _('Pending Admin Approval')),
        ('approved', _('Approved')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=100)
    buyer_contact = models.CharField(max_length=20)
    address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_admin_approval')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.product.title}"


class DigiCourse(models.Model):
    LANGUAGE_CHOICES = [
        ('hindi', _('Hindi')),
        ('english', _('English')),
        ('regional', _('Regional Language')),
    ]
    
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class DigiProgress(models.Model):
    shg = models.ForeignKey(SHG, on_delete=models.CASCADE)
    course = models.ForeignKey(DigiCourse, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shg', 'course']
    
    def __str__(self):
        return f"{self.shg.name} - {self.course.title}"


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Buyer: {self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('market:buyer_profile')


class ForecastNotification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    target_shgs = models.ManyToManyField(SHG, related_name='forecast_targets', blank=True)
    read_by = models.ManyToManyField(SHG, related_name='forecast_read', blank=True)
    
    def __str__(self):
        return self.title


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.title} by {self.user.username}"
