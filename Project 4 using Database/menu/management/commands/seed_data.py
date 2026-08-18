from django.core.management.base import BaseCommand

from menu.models import Category, MenuItem

MENU = {
    "Starters": [
        ("Garlic Bread", "Toasted with butter and garlic", 4.50, "🍞"),
        ("Bruschetta", "Tomato, basil and olive oil on toast", 5.00, "🍅"),
        ("Chicken Wings", "Spicy BBQ sauce", 7.50, "🍗"),
        ("Soup of the Day", "Ask the waiter!", 4.00, "🍲"),
    ],
    "Mains": [
        ("Margherita Pizza", "Tomato, mozzarella, basil", 9.50, "🍕"),
        ("Pepperoni Pizza", "Loaded with pepperoni", 11.00, "🍕"),
        ("Spaghetti Bolognese", "Slow-cooked beef ragu", 10.50, "🍝"),
        ("Cheeseburger", "Beef patty, cheddar, fries", 8.90, "🍔"),
        ("Grilled Salmon", "With lemon butter sauce", 13.50, "🐟"),
        ("Veggie Curry", "Chickpeas, spinach, coconut milk", 9.00, "🍛"),
    ],
    "Desserts": [
        ("Chocolate Brownie", "Warm, with ice cream", 5.50, "🍫"),
        ("Cheesecake", "Classic baked, berry compote", 5.00, "🍰"),
    ],
    "Drinks": [
        ("Fresh Orange Juice", "Squeezed to order", 3.50, "🍊"),
        ("Espresso", "Double shot", 2.00, "☕"),
        ("Iced Tea", "With lemon", 3.00, "🧊"),
        ("Sparkling Water", "Chilled bottle", 2.50, "💧"),
    ],
}


class Command(BaseCommand):
    help = "Seed the database with categories and menu items."

    def handle(self, *args, **options):
        for order, (category_name, items) in enumerate(MENU.items()):
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"emoji": items[0][3][:1], "order": order},
            )
            for name, description, price, emoji in items:
                MenuItem.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "description": description,
                        "price": price,
                        "emoji": emoji,
                    },
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Category.objects.count()} categories and "
                f"{MenuItem.objects.count()} menu items."
            )
        )