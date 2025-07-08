from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import IngredientForm, MealForm
from .models import FoodItem, MealEntry, ScheduleEntry, _calculate_macros
import json


def get_meal_plan_context(user):
    DAYS_OF_WEEK = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    food_item_qs = FoodItem.objects.filter(owner=user)
    schedule_entry_qs = ScheduleEntry.objects.filter(user=user)

    meals_by_day = {d: [] for d in DAYS_OF_WEEK}
    macros_by_day = {
        day: {"calories": 0.0, "protein": 0.0, "fats": 0.0, "carbs": 0.0}
        for day in DAYS_OF_WEEK
    }

    for schedule_entry in schedule_entry_qs:
        day = schedule_entry.day
        meals_by_day[day].append(schedule_entry)

        if schedule_entry.food_item:
            macros = schedule_entry.food_item.macro_totals()
            factor = schedule_entry.quantity
            for k in macros_by_day[day]:
                macros_by_day[day][k] += macros[k] * factor

    return {
        "food_items": food_item_qs,
        "days_of_week": DAYS_OF_WEEK,
        "meals_by_day": meals_by_day,
        "macros_by_day": macros_by_day,
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
    print(food_item_pk)
    if food_item_pk:
        food_item = get_object_or_404(FoodItem, pk=food_item_pk, owner=request.user)
        is_meal = food_item.is_meal
        entries = food_item.entries.all()
        macros = food_item.macro_totals()
        action_url_name = "edit_food_item"
    else:
        is_meal = False
        food_item = None
        entries = []
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
            "food_item": food_item,
            "entries": entries,
            "macros": macros,
            "action_url_name": action_url_name,
        },
    )


def save_food_item_from_form(request, form, food_item=None):
    is_meal = request.POST.get("is_meal") == "true"

    food_item = form.save(commit=False)
    food_item.owner = request.user
    food_item.is_meal = is_meal
    food_item.save()

    if is_meal:
        # Remove old entries if editing
        if food_item.pk:
            food_item.entries.all().delete()

        names = request.POST.getlist("ingredient_name")
        quantities = request.POST.getlist("ingredient_quantity")

        for name, quantity_str in zip(names, quantities):
            ingredient = FoodItem.objects.filter(
                owner=request.user, name__iexact=name, is_meal=False
            ).first()
            if not ingredient:
                continue

            try:
                quantity = float(quantity_str)
            except ValueError:
                quantity = 1

            MealEntry.objects.create(meal=food_item, item=ingredient, quantity=quantity)

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

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_POST
@login_required
def edit_food_item(request, food_item_pk):
    food_item = get_object_or_404(FoodItem, pk=food_item_pk, owner=request.user)
    is_meal = request.POST.get("is_meal") == "true"
    form = (
        MealForm(request.POST, instance=food_item)
        if is_meal
        else IngredientForm(request.POST, instance=food_item)
    )

    if form.is_valid():
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

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_POST
@login_required
def delete_food_item(request, pk):
    food_item = get_object_or_404(
        FoodItem,
        pk=pk,
        owner=request.user,
    )
    food_item.delete()

    context = get_meal_plan_context(request.user)
    html_library = render_to_string("piecemeal_app/partials/library.html", context)
    return JsonResponse(
        {
            "success": True,
            "html_library": html_library,
        },
    )


@require_POST
@login_required
def create_schedule_entry(request, day):
    _ = ScheduleEntry.objects.create(
        user=request.user, day=day, quantity=1, food_item=None
    )

    context = get_meal_plan_context(request.user)
    context["schedule_entries"] = context["meals_by_day"][day]
    context["day"] = day
    html_day_plan = render_to_string("piecemeal_app/partials/day_plan.html", context)
    return JsonResponse({"success": True, "html_day_plan": html_day_plan, "day": day})


@require_POST
@login_required
def update_schedule_entry(request):
    day = request.POST.get("day")
    entry_id = request.POST.get("entry_id")
    name = request.POST.get("name")
    quantity = request.POST.get("quantity")

    entry = ScheduleEntry.objects.get(id=entry_id, user=request.user)

    # Update quantity
    try:
        entry.quantity = float(quantity)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid quantity"}, status=400)

    # Update food item
    if name:
        try:
            food_item = FoodItem.objects.get(name__iexact=name, owner=request.user)
            entry.food_item = food_item
        except FoodItem.DoesNotExist:
            # Clear the food item if not found
            entry.food_item = None
            return JsonResponse(
                {"success": False, "error": "Food item not found"}, status=400
            )

    entry.save()

    context = get_meal_plan_context(request.user)
    context["schedule_entries"] = context["meals_by_day"][day]
    context["day_macros"] = context["macros_by_day"][day]
    context["day"] = day
    html_day_plan = render_to_string("piecemeal_app/partials/day_plan.html", context)
    return JsonResponse({"success": True, "html_day_plan": html_day_plan})


@require_POST
@login_required
def delete_schedule_entry(request, pk, day):
    schedule_entry = get_object_or_404(
        ScheduleEntry,
        pk=pk,
        user=request.user,
    )
    schedule_entry.delete()

    context = get_meal_plan_context(request.user)
    context["schedule_entries"] = context["meals_by_day"][day]
    context["day_macros"] = context["macros_by_day"][day]
    context["day"] = day
    html_day_plan = render_to_string("piecemeal_app/partials/day_plan.html", context)
    return JsonResponse({"success": True, "html_day_plan": html_day_plan, "day": day})


@require_POST
@login_required
def calculate_macros(request):
    data = json.loads(request.body)
    ingredients = data.get("ingredients", [])
    macros = _calculate_macros(request.user, ingredients)
    return JsonResponse(macros)
