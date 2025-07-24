from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.home, name="home"),
    path(
        "piecemeal/login/",
        auth_views.LoginView.as_view(template_name="piecemeal_app/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("piecemeal/", views.home, name="home"),
    path("piecemeal/signup/", views.signup, name="signup"),
    path(
        "piecemeal/food_item/form/",
        views.get_food_item_form,
        name="get_create_food_item",
    ),
    path(
        "piecemeal/food_item/form/<int:food_item_pk>/",
        views.get_food_item_form,
        name="get_edit_food_item",
    ),
    path(
        "piecemeal/food_item/create/",
        views.create_food_item,
        name="create_food_item",
    ),
    path(
        "piecemeal/food_item/edit/<int:food_item_pk>/",
        views.edit_food_item,
        name="edit_food_item",
    ),
    path(
        "piecemeal/food_item/delete/<int:pk>",
        views.delete_food_item,
        name="delete_food_item",
    ),
    path(
        "piecemeal/schedule_entry/form/",
        views.get_schedule_entry_form,
        name="get_create_schedule_entry",
    ),
    path(
        "piecemeal/schedule_entry/form/<int:entry_id>/",
        views.get_schedule_entry_form,
        name="get_edit_schedule_entry",
    ),
    path(
        "piecemeal/schedule_entry/create/",
        views.create_schedule_entry,
        name="create_schedule_entry",
    ),
    path(
        "piecemeal/schedule_entry/update/<int:entry_id>",
        views.update_schedule_entry,
        name="update_schedule_entry",
    ),
    path(
        "piecemeal/unschedule/<int:pk>/",
        views.delete_schedule_entry,
        name="delete_schedule_entry",
    ),
    path(
        "piecemeal/calculate_macros/",
        views.calculate_macros,
        name="calculate_macros",
    ),
    path(
        "piecemeal/calculate_macros_schedule_item/",
        views.calculate_macros_schedule_item,
        name="calculate_macros_schedule_item",
    ),
    path("piecemeal/grocery_list/", views.grocery_list, name="grocery_list"),
    path("piecemeal/autocomplete/", views.autocomplete, name="autocomplete"),
    path("piecemeal/search/", views.search, name="search"),
]
