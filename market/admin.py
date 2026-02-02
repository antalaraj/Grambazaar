from django.contrib import admin
from .models import SHG, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "shg", "price", "status", "category", "inventory", "created_at")
    list_filter = ("status", "category", "shg")
    search_fields = ("title", "shg__name")
    list_editable = ("status", "inventory", "price")
    ordering = ("-created_at",)


@admin.register(SHG)
class SHGAdmin(admin.ModelAdmin):
    list_display = ("name", "verification_level", "wallet_balance", "city", "state")
    search_fields = ("name", "city", "state")
