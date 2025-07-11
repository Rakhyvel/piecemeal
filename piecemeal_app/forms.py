from django import forms
from .models import FoodItem, ScheduleEntry


class IngredientForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["name", "calories", "protein", "carbs", "fats"]


class MealForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["name"]


class ScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = ScheduleEntry
        fields = ["quantity"]
