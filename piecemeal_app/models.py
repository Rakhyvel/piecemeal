from django.db import models
from django.contrib.auth.models import User


# Stores macros directly
class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_items")

    is_meal = models.BooleanField(default=False)
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)

    def macro_totals(self):
        if not self.is_meal:
            return {
                "calories": self.calories,
                "protein": self.protein,
                "carbs": self.carbs,
                "fats": self.fats,
            }
        else:
            total = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
            for entry in self.entries.all():
                child_macros = entry.item.macro_totals()
                factor = entry.quantity
                for k in total:
                    total[k] += child_macros[k] * factor
            return total


def _calculate_macros(user, ingredients: list[dict]) -> dict:
    total = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    for ingredient in ingredients:
        food_item = FoodItem.objects.get(name__iexact=ingredient["name"], owner=user)
        child_macros = food_item.macro_totals()
        factor = float(ingredient["quantity"])
        for k in total:
            total[k] += child_macros[k] * factor
    return total


class MealEntry(models.Model):
    meal = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="entries")
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)


class ScheduleEntry(models.Model):
    DAY_CHOICES = [
        ("saved", "Saved"),
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(
        FoodItem, null=True, blank=True, on_delete=models.SET_NULL
    )
    quantity = models.FloatField(default=1)
    day = models.CharField(max_length=10)

    def macro_totals(self):
        if not self.food_item:
            return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        food_item_macros = self.food_item.macro_totals()

        return {
            "calories": self.quantity * food_item_macros["calories"],
            "protein": self.quantity * food_item_macros["protein"],
            "fat": self.quantity * food_item_macros["fats"],
            "carbs": self.quantity * food_item_macros["carbs"],
        }
