from django import forms
from .models import FoodItem, ScheduleEntry, UNIT_CHOICES


class IngredientForm(forms.ModelForm):
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select unit-select"}),
    )

    class Meta:
        model = FoodItem
        fields = [
            "quantity",
            "unit",
            "name",
            "is_public",
            "aisle",
            "calories",
            "protein",
            "carbs",
            "fats",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the default unit to grams for ingredients
        if not self.instance.pk:
            self.fields["unit"].initial = "g"
        self.fields["quantity"].required = True

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is None or quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not self.instance.pk:
            try:
                FoodItem.objects.get(name__iexact=name)
                raise forms.ValidationError("Duplicate name detected.")
            except FoodItem.DoesNotExist:
                pass
        return name

    def _assert_non_negative(self, field_name):
        field = self.cleaned_data.get(field_name)
        if field is None or field < 0:
            raise forms.ValidationError(
                f"{field_name.title()} must be a non-negative number."
            )
        return field

    def clean_calories(self):
        return self._assert_non_negative("calories")

    def clean_protein(self):
        return self._assert_non_negative("protein")

    def clean_fats(self):
        return self._assert_non_negative("fats")

    def clean_carbs(self):
        return self._assert_non_negative("carbs")


class MealForm(forms.ModelForm):

    class Meta:
        model = FoodItem
        fields = ["name", "makes", "is_public"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not self.instance.pk:
            try:
                FoodItem.objects.get(name__iexact=name)
                raise forms.ValidationError("Duplicate name detected.")
            except FoodItem.DoesNotExist:
                pass
        return name

    def clean_makes(self):
        makes = self.cleaned_data.get("makes")
        if makes is None or makes <= 0:
            raise forms.ValidationError(f"Servings made must be a non-negative number.")
        return makes
