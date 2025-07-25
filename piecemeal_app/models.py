from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


EMPTY_MACROS = {
    "calories": 0.0,
    "protein": 0.0,
    "fats": 0.0,
    "carbs": 0.0,
    "fiber": 0.0,
}

UNIT_CHOICES = [
    (
        "Weight",
        [
            ("g", "g"),
            ("oz", "oz"),
            ("kg", "kg"),
            ("lb", "lb"),
        ],
    ),
    (
        "Volume",
        [
            ("tsp", "tsp"),
            ("tbsp", "tbsp"),
            ("cup", "cup"),
            ("L", "L"),
            ("mL", "mL"),
        ],
    ),
    (
        "Count",
        [
            ("servings", "servings"),
            ("each", "each"),
        ],
    ),
]

UNIT_CONVERSIONS = {
    "g": {
        "g": 1,
        "kg": 0.001,
        "oz": 0.03527396,
        "lb": 0.00220462,
    },
    "kg": {
        "g": 1000,
        "kg": 1,
        "oz": 35.27396,
        "lb": 2.20462,
    },
    "oz": {
        "g": 28.3495,
        "kg": 0.0283495,
        "oz": 1,
        "lb": 0.0625,
    },
    "lb": {
        "g": 453.592,
        "kg": 0.453592,
        "oz": 16,
        "lb": 1,
    },
    "tsp": {
        "tsp": 1,
        "tbsp": 1 / 3,
        "cup": 1 / 48,
    },
    "tbsp": {
        "tsp": 3,
        "tbsp": 1,
        "cup": 1 / 16,
    },
    "cup": {
        "tsp": 48,
        "tbsp": 16,
        "cup": 1,
    },
}


AISLES = [
    ("produce", "🍎 Produce"),
    ("bakery", "🍞 Bakery"),
    ("frozen", "🧊 Frozen"),
    ("sauce", "🍶 Condiments & Sauces"),
    ("deli", "🍗 Deli"),
    ("canned", "🥫 Canned"),
    ("health", "💊 Vitamins & Supplements"),
    ("baking", "🥣 Baking & Spices"),
    ("pasta", "🍝 Pasta, Rice & Grains"),
    ("dry", "🍽 Dry & Staple Foods"),
    ("snacks", "🍪 Snacks"),
    ("beverages", "🧃 Beverages"),
    ("dairy", "🥛 Dairy"),
    ("other", "Other"),
]


# a food item can be either an ingredient (direct macros) or a meal (list of MealEntry's, macros summed)
class FoodItem(models.Model):
    # both ingredient and meal fields
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="food_items"
    )
    quantity = models.FloatField(default=0)
    unit = models.CharField(
        max_length=10,
        choices=[(val, label) for _, group in UNIT_CHOICES for val, label in group],
    )
    is_meal = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    # ingredient specific fields
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    aisle = MultiSelectField(choices=AISLES, default="other")
    common_csv_filename = models.CharField(max_length=20, default="")

    # meal specific fields
    makes = models.FloatField(default=1.0)

    def macro_totals(self):
        if not self.is_meal:
            return {
                "calories": self.calories,
                "protein": self.protein,
                "carbs": self.carbs,
                "fats": self.fats,
                "fiber": self.fiber,
            }
        else:
            total = EMPTY_MACROS.copy()
            for entry in self.entries.all():
                food_item = entry.item
                food_item_unit = food_item.unit
                food_item_quantity = food_item.quantity
                ingredient_unit = entry.unit
                unit_conversion_factor = get_unit_conversion_factor(
                    ingredient_unit, food_item_unit
                )
                child_macros = food_item.macro_totals()
                # 50 g = 100 cal
                # 1 kg = ? cal
                # 1000 g = ? cal
                # 1000 g = (1000 / 50) * 100 cal
                factor = (
                    float(entry.quantity)
                    * unit_conversion_factor
                    / (food_item_quantity * self.makes)
                )
                for k in total:
                    total[k] += child_macros[k] * factor
            return total

    def get_dict(self):
        return {
            "id": self.pk,
            "name": self.name,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fats": self.fats,
            "fiber": self.fiber,
            "aisle": self.aisle,
            "is_public": self.is_public,
            "quantity": self.quantity,
            "makes": self.makes,
        }

    def get_ingredients(self):
        """
        "name": String,
        "quantity": Float,
        "macros": {
            "calories": Float,
            "protein": Float,
            "carbs": Float,
            "fat": Float,
            "fiber": Float,
        }
        """
        retval = []
        entries: list[MealEntry] = self.entries.all()
        for entry in entries:
            retval.append(
                {
                    "name": entry.item.name,
                    "quantity": entry.quantity,
                    "macros": entry.item.get_macros_adjusted_with_unit(
                        entry.quantity / self.makes, entry.unit
                    ),
                    "unit": entry.unit,
                    "compatible_units": get_compatible_units(entry.item.unit),
                }
            )
        return retval

    def furnish_grocery_list(self, grocery_list, quantity, unit):
        factor = get_unit_conversion_factor(unit, self.unit)
        if not self.is_meal:
            if self not in grocery_list:
                grocery_list[self] = {"quantity": 0.0, "unit": self.unit}
            factor = get_unit_conversion_factor(unit, self.unit)
            grocery_list[self]["quantity"] += quantity * factor
        else:
            for entry in self.entries.all():
                entry.item.furnish_grocery_list(
                    grocery_list,
                    factor * quantity * entry.quantity / self.makes,
                    entry.unit,
                )

    def get_compatible_choices(self):
        retval = [
            category
            for category in UNIT_CHOICES
            if (self.unit, self.unit) in category[1]
        ]
        return retval

    def get_macros_adjusted_with_unit(self, quantity: float, unit: str):
        macros = self.macro_totals()
        unit_conversion_factor = get_unit_conversion_factor(unit, self.unit)
        factor = quantity * unit_conversion_factor / self.quantity
        for k in macros:
            macros[k] *= factor
        return macros


def sum_total_macros(user, ingredients: list[dict], makes: float) -> dict:
    total = EMPTY_MACROS.copy()
    for ingredient in ingredients:
        try:
            food_item = FoodItem.objects.get(name__iexact=ingredient["name"])
        except FoodItem.DoesNotExist:
            continue
        food_item_unit = food_item.unit
        food_item_quantity = food_item.quantity
        ingredient_unit = ingredient["unit"]
        unit_conversion_factor = get_unit_conversion_factor(
            ingredient_unit, food_item_unit
        )
        child_macros = food_item.macro_totals()
        # 50 g = 100 cal
        # 1 kg = ? cal
        # 1000 g = ? cal
        # 1000 g = (1000 / 50) * 100 cal
        factor = (
            float(ingredient["quantity"])
            * unit_conversion_factor
            / (food_item_quantity * makes)
        )
        for k in total:
            total[k] += child_macros[k] * factor
    return total


def get_unit_conversion_factor(unit_from: str, unit_to: str) -> float:
    if unit_from == unit_to:
        return 1.0

    try:
        return UNIT_CONVERSIONS[unit_from][unit_to]
    except KeyError:
        try:
            return 1.0 / UNIT_CONVERSIONS[unit_to][unit_from]
        except KeyError:
            raise ValueError(
                f"Cannot convert between incompatible units: {unit_from} → {unit_to}"
            )


def get_compatible_units(unit_from: str) -> list[str]:
    compatible = set(
        UNIT_CONVERSIONS.get(unit_from, {unit_from: {unit_from: 1.0}}).keys()
    )
    for src_unit, targets in UNIT_CONVERSIONS.items():
        if unit_from in targets:
            compatible.add(src_unit)
    return list(compatible)


class MealEntry(models.Model):
    meal = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="entries")
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    unit = models.CharField(
        max_length=10,
        choices=[(val, label) for _, group in UNIT_CHOICES for val, label in group],
    )


class ScheduleEntry(models.Model):
    DAYS_OF_WEEK = [
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
    unit = models.CharField(
        max_length=10,
        choices=[(val, label) for _, group in UNIT_CHOICES for val, label in group],
    )
    days = MultiSelectField(choices=DAYS_OF_WEEK)

    def macro_totals(self):
        if not self.food_item:
            return EMPTY_MACROS

        return self.food_item.get_macros_adjusted_with_unit(self.quantity, self.unit)
