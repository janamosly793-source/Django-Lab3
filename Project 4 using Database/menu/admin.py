from django.contrib import admin

from .models import Category, MenuItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "emoji", "order"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "available"]
    list_filter = ["category", "available"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "total", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]


admin.site.register(OrderItem)