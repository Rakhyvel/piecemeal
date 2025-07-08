from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("food_item/form/", views.get_food_item_form, name="get_create_food_item"),
    path(
        "food_item/form/<int:food_item_pk>/",
        views.get_food_item_form,
        name="get_edit_food_item",
    ),
    path(
        "food_item/create/",
        views.create_food_item,
        name="create_food_item",
    ),
    path(
        "food_item/edit/<int:food_item_pk>/",
        views.edit_food_item,
        name="edit_food_item",
    ),
    path(
        "food_item/delete/<int:pk>",
        views.delete_food_item,
        name="delete_food_item",
    ),
    path(
        "schedule_entry/create/<str:day>/",
        views.create_schedule_entry,
        name="create_schedule_entry",
    ),
    path(
        "schedule_entry/update/",
        views.update_schedule_entry,
        name="update_schedule_entry",
    ),
    path(
        "unschedule/<int:pk>/<str:day>/",
        views.delete_schedule_entry,
        name="delete_schedule_entry",
    ),
    path("calculate_macros/", views.calculate_macros, name="calculate_macros"),
]
