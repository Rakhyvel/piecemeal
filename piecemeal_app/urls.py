from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("increment/", views.increment_counter, name="increment"),
    path(
        "food_item/create/",
        views.create_food_item_ajax,
        name="create_food_item_ajax",
    ),
    path("food_item/delete/<int:pk>/", views.delete_food_item, name="delete_food_item"),
]
