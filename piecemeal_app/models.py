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

    def total_macros(self):
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
                child_macros = entry.item.total_macros()
                factor = entry.quantity
                for k in total:
                    total[k] += child_macros[k] * factor
            return total


class MealEntry(models.Model):
    meal = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="entries")
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
