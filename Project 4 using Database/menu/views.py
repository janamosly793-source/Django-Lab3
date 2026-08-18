from decimal import Decimal

from django.db import transaction
from django.db.models import Count, F, Sum
from django.shortcuts import redirect, render

from .models import Category, MenuItem, Order, OrderItem

CART_KEY = "cart"


def _cart(request):
    return request.session.setdefault(CART_KEY, {})


def _save_cart(request, cart):
    request.session[CART_KEY] = cart
    request.session.modified = True


def _cart_count(cart):
    return sum(cart.values())


def menu(request):
    selected = request.GET.get("cat")
    items = MenuItem.objects.filter(available=True)
    if selected:
        items = items.filter(category_id=selected)
    categories = Category.objects.all()
    items_by_category = {}
    for category in categories:
        group = [i for i in items if i.category_id == category.id]
        if group:
            items_by_category[category] = group
    return render(request, "menu/menu.html", {
        "categories": categories,
        "items_by_category": items_by_category,
        "selected": selected,
        "cart_count": _cart_count(_cart(request)),
    })


def cart(request):
    cart = _cart(request)
    quantities = []
    total = Decimal("0.00")
    for item_id, qty in cart.items():
        item = MenuItem.objects.filter(id=item_id, available=True).first()
        if item:
            line_total = item.price * qty
            quantities.append((item, qty, line_total))
            total += line_total

    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("item_id")
        if action == "add":
            if item_id and MenuItem.objects.filter(id=item_id, available=True).exists():
                cart[item_id] = cart.get(item_id, 0) + 1
                _save_cart(request, cart)
                return redirect(request.POST.get("next") or "cart")
        elif action == "remove":
            cart.pop(item_id, None)
            _save_cart(request, cart)
        elif action == "clear":
            cart.clear()
            _save_cart(request, cart)

    return render(request, "menu/cart.html", {
        "quantities": quantities,
        "total": total,
        "cart_count": _cart_count(cart),
    })


@transaction.atomic
def checkout(request):
    cart = _cart(request)
    if request.method == "POST":
        customer = request.POST.get("customer", "").strip()[:50]
        if customer and cart:
            order = Order.objects.create(customer=customer)
            for item_id, qty in cart.items():
                item = MenuItem.objects.filter(id=item_id, available=True).first()
                if item:
                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        quantity=qty,
                        unit_price=item.price,
                    )
            cart.clear()
            _save_cart(request, cart)
            return redirect("order_detail", order_id=order.id)
        return render(request, "menu/checkout.html", {
            "error": "Please enter your name and add items to the cart.",
            "cart_count": _cart_count(cart),
        })
    return render(request, "menu/checkout.html", {"cart_count": _cart_count(cart)})


def orders(request):
    status = request.GET.get("status")
    all_orders = Order.objects.all()
    if status:
        all_orders = all_orders.filter(status=status)
    return render(request, "menu/orders.html", {
        "orders": all_orders,
        "status": status,
        "statuses": Order.STATUS_CHOICES,
        "cart_count": _cart_count(_cart(request)),
    })


def order_detail(request, order_id):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return redirect("orders")
    return render(request, "menu/order_detail.html", {
        "order": order,
        "cart_count": _cart_count(_cart(request)),
    })


def stats(request):
    revenue = OrderItem.objects.aggregate(
        total=Sum(F("unit_price") * F("quantity"))
    )["total"] or Decimal("0.00")
    revenue = revenue.quantize(Decimal("0.01"))
    popular = (
        OrderItem.objects.values("item__name")
        .annotate(ordered=Sum("quantity"))
        .order_by("-ordered")[:5]
    )
    by_category = (
        OrderItem.objects.values("item__category__name")
        .annotate(ordered=Sum("quantity"))
        .order_by("-ordered")
    )
    return render(request, "menu/stats.html", {
        "revenue": revenue,
        "order_count": Order.objects.count(),
        "popular": popular,
        "by_category": by_category,
        "cart_count": _cart_count(_cart(request)),
    })