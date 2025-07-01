from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.http import JsonResponse
from .forms import IngredientForm

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
    ingredients = request.user.food_items.all()
    return render(
        request,
        "piecemeal_app/home.html",
        {"item_count": item_count, "ingredients": ingredients},
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
            ingredient = form.save(commit=False)
            ingredient.owner = request.user
            ingredient.save()
            ingredients = request.user.food_items.all()
            return JsonResponse(
                {
                    "success": True,
                    "ingredient": {
                        "name": ingredient.name,
                        "id": ingredient.id,
                        "calories": ingredient.calories,
                    },
                    "item_count": ingredients.count(),
                },
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = IngredientForm()
        return render(
            request, "piecemeal_app/partials/ingredient_form.html", {"form": form}
        )
