from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("increment/", views.increment_counter, name="increment"),
    path(
        "ingredient/create/",
        views.create_ingredient_ajax,
        name="create_ingredient_ajax",
    ),
    path(
        "meal/create/",
        views.create_meal_ajax,
        name="create_meal_ajax",
    ),
    path("food_item/delete/<int:pk>/", views.delete_food_item, name="delete_food_item"),
]
