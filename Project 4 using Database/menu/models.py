from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    emoji = models.CharField(max_length=10, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ["category__order", "name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("paid", "Paid"),
    ]

    customer = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} - {self.customer}"

    @property
    def total(self):
        return sum(oi.line_total for oi in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.item.name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity