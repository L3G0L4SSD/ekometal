from django.contrib import admin

from .models import Category, ContactInquiry, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ("image", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("model_code", "name", "category", "is_featured", "created_at")
    list_filter = ("category", "is_featured")
    list_editable = ("is_featured",)
    search_fields = ("name", "model_code")
    inlines = [ProductImageInline]


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company_name", "phone", "product_interest", "created_at")
    search_fields = ("full_name", "company_name", "phone")
    readonly_fields = ("created_at",)
