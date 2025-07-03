from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import IngredientForm, MealForm
from .models import FoodItem, MealEntry

# from .models import UserCounter


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


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home(request):
    item_count = request.user.food_items.count()
    food_items = request.user.food_items.all()
    return render(
        request,
        "piecemeal_app/home.html",
        {"item_count": item_count, "food_items": food_items},
    )


@login_required
def increment_counter(request):
    # # counter, _ = UserCounter.objects.get_or_create(user=request.user)
    # counter.count += 1
    # print(counter.count)
    # counter.save()
    return redirect("home")


def create_ingredient_ajax(request):
    if request.method == "POST":
        form = IngredientForm(request.POST)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.is_meal = False
            food_item.owner = request.user
            food_item.save()
            food_items = request.user.food_items.all()
            html_list = render_to_string(
                "piecemeal_app/partials/food_item_list.html",
                {"food_items": FoodItem.objects.filter(owner=request.user)},
            )
            return JsonResponse(
                {
                    "success": True,
                    "html_list": html_list,
                    "item_count": food_items.count(),
                },
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = IngredientForm()
        return render(
            request, "piecemeal_app/partials/ingredient_form.html", {"form": form}
        )


def create_meal_ajax(request):
    if request.method == "POST":
        form = MealForm(request.POST, user=request.user)
        if form.is_valid():
            food = form.save(commit=False)
            food.is_meal = True
            food.owner = request.user
            food.save()
            food_items = request.user.food_items.all()
            for item in form.cleaned_data["entries"]:
                MealEntry.objects.create(meal=food, item=item, quantity=1)
            html_list = render_to_string(
                "piecemeal_app/partials/food_item_list.html",
                {"food_items": FoodItem.objects.filter(owner=request.user)},
            )
            return JsonResponse(
                {
                    "success": True,
                    "html_list": html_list,
                    "item_count": food_items.count(),
                },
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = MealForm(user=request.user)
        return render(request, "piecemeal_app/partials/meal_form.html", {"form": form})


@require_POST
def delete_food_item(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk, owner=request.user)
    food_item.delete()
    food_items = request.user.food_items.all()
    html_list = render_to_string(
        "piecemeal_app/partials/food_item_list.html",
        {"food_items": FoodItem.objects.filter(owner=request.user)},
    )
    return JsonResponse(
        {
            "success": True,
            "html_list": html_list,
            "item_count": food_items.count(),
        },
    )
