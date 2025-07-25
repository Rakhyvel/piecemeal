from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import IngredientForm, MealForm
from datetime import datetime
from django.db.models import Q
from .models import (
    FoodItem,
    MealEntry,
    ScheduleEntry,
    sum_total_macros,
    get_compatible_units,
    get_unit_conversion_factor,
    EMPTY_MACROS,
    UNIT_CHOICES,
    AISLES,
)
import json


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def get_meal_plan_context(user, search=""):
    if len(search) == 0:
        food_item_qs = FoodItem.objects.filter(Q(is_public=True) | Q(owner=user))
    else:
        food_item_qs = FoodItem.objects.filter(
            Q(name__icontains=search), Q(is_public=True) | Q(owner=user)
        )
    schedule_entry_qs = ScheduleEntry.objects.filter(user=user)

    meals_by_day = {d: [] for d in DAYS_OF_WEEK}
    macros_by_day = {day: EMPTY_MACROS.copy() for day in DAYS_OF_WEEK}

    for schedule_entry in schedule_entry_qs:
        for day in schedule_entry.days:
            meals_by_day[day.lower()].append(schedule_entry)

            if schedule_entry.food_item:
                macros = schedule_entry.macro_totals()
                for k in macros_by_day[day.lower()]:
                    macros_by_day[day.lower()][k] += macros[k]

    return {
        "food_items": food_item_qs,
        "days_of_week": DAYS_OF_WEEK,
        "meals_by_day": meals_by_day,
        "macros_by_day": macros_by_day,
        "timestamp": int(datetime.utcnow().timestamp()),
    }


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log them in automatically
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "piecemeal_app/signup.html", {"form": form})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home(request):
    context = get_meal_plan_context(request.user)
    return render(request, "piecemeal_app/home.html", context)


@login_required
def get_food_item_form(request, food_item_pk=None):
    if food_item_pk:
        food_item = get_object_or_404(FoodItem, pk=food_item_pk)
        is_meal = food_item.is_meal
        ingredients = food_item.get_ingredients()
        compatible_unit_choices = food_item.get_compatible_choices()
        macros = sum_total_macros(request.user, ingredients, food_item.makes)
        action_url_name = "edit_food_item"
    else:
        is_meal = request.GET.get("is_meal") == "true"
        food_item = None
        ingredients = []
        compatible_unit_choices = UNIT_CHOICES
        macros = None
        action_url_name = "create_food_item"

    if is_meal:
        (form_html_file, form) = "piecemeal_app/partials/meal_form.html", MealForm(
            instance=food_item
        )
    else:
        (form_html_file, form) = (
            "piecemeal_app/partials/ingredient_form.html",
            IngredientForm(instance=food_item),
        )

    return render(
        request,
        form_html_file,
        {
            "form": form,
            "food_item": food_item.get_dict() if food_item else None,
            "ingredients": ingredients,
            "macros": macros,
            "compatible_unit_choices": compatible_unit_choices,
            "action_url_name": action_url_name,
            "aisles": AISLES,
        },
    )


@login_required
def duplicate_food_item_form(request, food_item_pk):
    food_item = get_object_or_404(FoodItem, pk=food_item_pk)
    is_meal = food_item.is_meal
    ingredients = food_item.get_ingredients()
    compatible_unit_choices = food_item.get_compatible_choices()
    macros = sum_total_macros(request.user, ingredients, food_item.makes)
    action_url_name = "create_food_item"

    food_item_dict = food_item.get_dict()
    food_item_dict["id"] = None
    food_item_dict["name"] = ""

    if is_meal:
        (form_html_file, form) = "piecemeal_app/partials/meal_form.html", MealForm(
            instance=None
        )
    else:
        (form_html_file, form) = (
            "piecemeal_app/partials/ingredient_form.html",
            IngredientForm(instance=None),
        )

    return render(
        request,
        form_html_file,
        {
            "form": form,
            "food_item": food_item_dict,
            "ingredients": ingredients,
            "macros": macros,
            "compatible_unit_choices": compatible_unit_choices,
            "action_url_name": action_url_name,
            "aisles": AISLES,
        },
    )


@login_required
def get_schedule_entry_form(request, entry_id=None):
    if entry_id:
        schedule_entry = get_object_or_404(
            ScheduleEntry, pk=entry_id, user=request.user
        )
        food_item = schedule_entry.food_item
        if food_item:
            compatible_units = get_compatible_units(food_item.unit)
        else:
            compatible_units = []
        macros = schedule_entry.macro_totals()
        ingredient_unit = schedule_entry.unit
        action_url_name = "update_schedule_entry"
    else:
        schedule_entry = None
        macros = EMPTY_MACROS.copy()
        action_url_name = "create_schedule_entry"
        compatible_units = []
        ingredient_unit = ""

    test = render(
        request,
        "piecemeal_app/partials/schedule_entry_form.html",
        {
            "schedule_entry": schedule_entry,
            "action_url_name": action_url_name,
            "compatible_units": compatible_units,
            "ingredient_unit": ingredient_unit,
            "macros": macros,
            "days_of_week": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
        },
    )
    return test


def save_food_item_from_form(
    request, form: IngredientForm | MealForm, food_item=None
) -> FoodItem:
    is_meal = request.POST.get("is_meal") == "true"

    food_item = form.save(commit=False)
    food_item.owner = request.user
    food_item.is_meal = is_meal
    if is_meal:
        food_item.unit = "servings"
        food_item.quantity = 1
    food_item.save()

    if is_meal:
        # Remove old entries if editing
        if food_item.pk:
            food_item.entries.all().delete()

        names = request.POST.getlist("ingredient_name")
        quantities = request.POST.getlist("ingredient_quantity")
        units = request.POST.getlist("ingredient_unit")

        for name, quantity_str, unit in zip(names, quantities, units):
            ingredient = FoodItem.objects.filter(name__iexact=name).first()

            if not ingredient:
                continue

            try:
                quantity = float(quantity_str)
            except ValueError:
                quantity = 1

            MealEntry.objects.create(
                meal=food_item, item=ingredient, quantity=quantity, unit=unit
            )

    return food_item


@require_POST
@login_required
def create_food_item(request):
    is_meal = request.POST.get("is_meal") == "true"
    form = MealForm(request.POST) if is_meal else IngredientForm(request.POST)

    if form.is_valid():
        save_food_item_from_form(request, form)

        context = get_meal_plan_context(request.user)
        html_library = render_to_string("piecemeal_app/partials/library.html", context)
        html_meal_plan = render_to_string(
            "piecemeal_app/partials/meal_plan.html", context
        )
        return JsonResponse(
            {
                "success": True,
                "html_library": html_library,
                "html_meal_plan": html_meal_plan,
            }
        )

    errors = list(form.errors.keys())
    return JsonResponse(
        {
            "success": False,
            "field_errors": errors,
        }
    )


@require_POST
@login_required
def edit_food_item(request, food_item_pk):
    food_item = get_object_or_404(FoodItem, pk=food_item_pk)
    is_meal = request.POST.get("is_meal") == "true"
    form = (
        MealForm(request.POST, instance=food_item)
        if is_meal
        else IngredientForm(request.POST, instance=food_item)
    )

    if form.is_valid() and request.user == food_item.owner:
        save_food_item_from_form(request, form, food_item)

        context = get_meal_plan_context(request.user)
        html_library = render_to_string("piecemeal_app/partials/library.html", context)
        html_meal_plan = render_to_string(
            "piecemeal_app/partials/meal_plan.html", context
        )
        return JsonResponse(
            {
                "success": True,
                "html_library": html_library,
                "html_meal_plan": html_meal_plan,
            }
        )

    errors = list(form.errors.keys())
    return JsonResponse(
        {
            "success": False,
            "field_errors": errors,
        }
    )


@require_POST
@login_required
def delete_food_item(request, pk):
    food_item = get_object_or_404(
        FoodItem,
        pk=pk,
    )
    food_item.delete()

    context = get_meal_plan_context(request.user)
    html_library = render_to_string("piecemeal_app/partials/library.html", context)
    html_meal_plan = render_to_string("piecemeal_app/partials/meal_plan.html", context)
    return JsonResponse(
        {
            "success": True,
            "html_library": html_library,
            "html_meal_plan": html_meal_plan,
        },
    )


@require_POST
@login_required
def create_schedule_entry(request):
    name = request.POST.get("name")
    quantity = float(request.POST.get("quantity"))
    unit = request.POST.get("unit")
    days = request.POST.getlist("days")

    if len(days) == 0:
        return JsonResponse({"success": False, "error": "No days selected"}, status=400)

    try:
        food_item = FoodItem.objects.get(name__iexact=name)
    except FoodItem.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Food item not found"}, status=400
        )

    _ = ScheduleEntry.objects.create(
        user=request.user, days=days, quantity=quantity, food_item=food_item, unit=unit
    )

    context = get_meal_plan_context(request.user)
    html_meal_plan = render_to_string("piecemeal_app/partials/meal_plan.html", context)
    return JsonResponse({"success": True, "html_meal_plan": html_meal_plan})


@require_POST
@login_required
def update_schedule_entry(request, entry_id):
    name = request.POST.get("name")
    quantity = request.POST.get("quantity")
    unit = request.POST.get("unit")
    days = request.POST.getlist("days")

    if len(days) == 0:
        return delete_schedule_entry(request, entry_id)

    entry = ScheduleEntry.objects.get(id=entry_id, user=request.user)

    entry.unit = unit
    entry.days = days

    # Update quantity
    try:
        entry.quantity = float(quantity)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid quantity"}, status=400)

    # Update food item
    if name:
        try:
            food_item = FoodItem.objects.get(name__iexact=name)
            entry.food_item = food_item
        except FoodItem.DoesNotExist:
            # Clear the food item if not found
            entry.food_item = None
            return JsonResponse(
                {"success": False, "error": "Food item not found"}, status=400
            )

    entry.save()

    context = get_meal_plan_context(request.user)
    html_meal_plan = render_to_string("piecemeal_app/partials/meal_plan.html", context)
    return JsonResponse({"success": True, "html_meal_plan": html_meal_plan})


@require_POST
@login_required
def delete_schedule_entry(request, pk):
    schedule_entry = get_object_or_404(
        ScheduleEntry,
        pk=pk,
        user=request.user,
    )
    schedule_entry.delete()

    context = get_meal_plan_context(request.user)
    html_meal_plan = render_to_string("piecemeal_app/partials/meal_plan.html", context)
    return JsonResponse({"success": True, "html_meal_plan": html_meal_plan})


@require_POST
@login_required
def calculate_macros(request):
    def decorate_with_macros(ingredients, makes):
        for ingredient in ingredients:
            try:
                try:
                    quantity = float(ingredient["quantity"])
                except ValueError:
                    quantity = 0.0
                    ingredient["quantity"] = 0.0
                name = ingredient["name"]
                food_item = FoodItem.objects.get(name__iexact=name)
                unit = ingredient["unit"]
                compatible_units = get_compatible_units(food_item.unit)
                if unit not in compatible_units:
                    unit = compatible_units[0]
                ingredient["macros"] = food_item.get_macros_adjusted_with_unit(
                    quantity / makes, unit
                )
                ingredient["unit"] = unit
                ingredient["compatible_units"] = compatible_units
            except FoodItem.DoesNotExist:
                pass

    data = json.loads(request.body)
    ingredients = data.get("ingredients", [])
    makes_str = data.get("makes", 1)
    makes = float(makes_str) if len(makes_str) > 0 else 1
    decorate_with_macros(ingredients, makes)
    macros = sum_total_macros(request.user, ingredients, makes)
    html_meal_ingredients_list = render_to_string(
        "piecemeal_app/partials/meal_ingredients_list.html",
        {
            "ingredients": ingredients,
            "macros": macros,
        },
    )
    return JsonResponse(
        {"success": True, "html_meal_ingredients_list": html_meal_ingredients_list}
    )


@require_POST
@login_required
def calculate_macros_schedule_item(request):
    name = request.POST.get("name")
    unit = request.POST.get("unit")
    food_item = FoodItem.objects.get(name__iexact=name)

    try:
        quantity = float(request.POST.get("quantity"))
        macros = food_item.get_macros_adjusted_with_unit(quantity, unit)
    except ValueError:
        macros = EMPTY_MACROS.copy()

    compatible_units = get_compatible_units(food_item.unit)
    if unit not in compatible_units:
        unit = compatible_units[0]

    html_macros = render_to_string(
        "piecemeal_app/partials/schedule_entry_form_macros.html",
        {
            "macros": macros,
        },
    )
    html_units = render_to_string(
        "piecemeal_app/partials/schedule_entry_form_units.html",
        {
            "ingredient_unit": unit,
            "compatible_units": compatible_units,
        },
    )
    return JsonResponse(
        {"success": True, "html_macros": html_macros, "html_units": html_units}
    )


def grocery_list(request):
    schedule_entries = ScheduleEntry.objects.filter(user=request.user)

    grocery_list = dict()
    for entry in schedule_entries:
        if not entry.food_item:
            continue
        entry.food_item.furnish_grocery_list(
            grocery_list, entry.quantity * len(entry.days), entry.unit
        )

    categories = [(aisle, []) for aisle in AISLES]
    for item in grocery_list.keys():
        for i in range(len(categories)):
            if item.aisle[0] == categories[i][0][0]:
                categories[i][1].append((item, grocery_list[item]))

    html_grocery_list = render_to_string(
        "piecemeal_app/partials/grocery_list.html",
        {"categories": categories},
    )
    return JsonResponse({"success": True, "html_grocery_list": html_grocery_list})


@require_GET
def autocomplete(request):
    term = request.GET.get("term", "")
    own_results = FoodItem.objects.filter(name__icontains=term, owner=request.user)[:20]
    shared_results = FoodItem.objects.filter(
        name__icontains=term, is_public=True
    ).exclude(owner=request.user)[:20]

    data = []
    for item in own_results:
        data.append(
            {
                "label": f"{item.name}",
                "value": item.name,
            }
        )
    for item in shared_results:
        username = f"by {item.owner.username}" if item.owner else "common"
        data.append(
            {
                "label": f"{item.name} <em>({username})</em>",
                "value": item.name,
            }
        )

    return JsonResponse(data, safe=False)


@require_GET
@login_required
def search(request):
    query = request.GET.get("q", "")
    user = request.user
    context = get_meal_plan_context(user=user, search=query)
    html_library_food_item_list = render_to_string(
        "piecemeal_app/partials/library_food_item_list.html", context
    )
    return JsonResponse(
        {
            "success": True,
            "html_library_food_item_list": html_library_food_item_list,
        }
    )
