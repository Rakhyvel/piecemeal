from django import forms
from .models import FoodItem, ScheduleEntry, UNIT_CHOICES


class IngredientForm(forms.ModelForm):
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select unit-select"}),
    )

    class Meta:
        model = FoodItem
        fields = ["quantity", "unit", "name", "calories", "protein", "carbs", "fats"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the default unit to grams for ingredients
        if not self.instance.pk:
            self.fields["unit"].initial = "g"


class MealForm(forms.ModelForm):

    class Meta:
        model = FoodItem
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = ScheduleEntry
        fields = ["quantity"]
