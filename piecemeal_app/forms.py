from django import forms
from .models import FoodItem


class IngredientForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["name", "calories", "protein", "carbs", "fats"]


class MealForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["name"]
