from django.urls import path
from django.conf import settings
from . import views


urlpatterns = [
    path(settings.URL_PREFIX + "", views.home, name="home"),
    path(settings.URL_PREFIX + "piecemeal/", views.home, name="home"),
    path(settings.URL_PREFIX + "piecemeal/signup/", views.signup, name="signup"),
    path(
        settings.URL_PREFIX + "piecemeal/food_item/form/",
        views.get_food_item_form,
        name="get_create_food_item",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/food_item/form/<int:food_item_pk>/",
        views.get_food_item_form,
        name="get_edit_food_item",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/food_item/create/",
        views.create_food_item,
        name="create_food_item",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/food_item/edit/<int:food_item_pk>/",
        views.edit_food_item,
        name="edit_food_item",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/food_item/delete/<int:pk>",
        views.delete_food_item,
        name="delete_food_item",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/schedule_entry/form/",
        views.get_schedule_entry_form,
        name="get_create_schedule_entry",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/schedule_entry/form/<int:entry_id>/",
        views.get_schedule_entry_form,
        name="get_edit_schedule_entry",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/schedule_entry/create/",
        views.create_schedule_entry,
        name="create_schedule_entry",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/schedule_entry/update/<int:entry_id>",
        views.update_schedule_entry,
        name="update_schedule_entry",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/unschedule/<int:pk>/",
        views.delete_schedule_entry,
        name="delete_schedule_entry",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/calculate_macros/",
        views.calculate_macros,
        name="calculate_macros",
    ),
    path(
        settings.URL_PREFIX + "piecemeal/calculate_macros_schedule_item/",
        views.calculate_macros_schedule_item,
        name="calculate_macros_schedule_item",
    ),
]
