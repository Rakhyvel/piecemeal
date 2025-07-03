from django import forms
from .models import FoodItem


class IngredientForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["name", "calories", "protein", "carbs", "fats"]


class MealForm(forms.ModelForm):
    entries = forms.ModelMultipleChoiceField(
        queryset=FoodItem.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Ingredients for this meal",
    )

    class Meta:
        model = FoodItem
        fields = ["name", "entries"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["entries"].queryset = FoodItem.objects.filter(owner=user)
