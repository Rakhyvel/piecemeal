from django import forms
from .models import IngredientModel


class IngredientForm(forms.ModelForm):
    class Meta:
        model = IngredientModel
        fields = ["name", "calories", "protein", "carbs", "fats"]
