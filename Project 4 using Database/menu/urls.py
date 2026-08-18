from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("stats/", views.stats, name="stats"),
]