// Get CSRF token from the cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function decodeHTMLEntities(text) {
    var txt = document.createElement("textarea");
    txt.innerHTML = text;
    return txt.value;
}
const csrftoken = getCookie('csrftoken');
var currentTab = "meal"

// Make it so that all headers have the CSRF token
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!(/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type))) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function () {
    $("#profile").hide()
    $(".meal-plan-container").show()
    $("#library").hide()
    $("#create-schedule-entry").show();
    $("#create-food-item").hide();
})

$(document).on("click", "#profile-tab-btn", function () {
    $("#profile").show()
    $(".meal-plan-container").hide()
    $("#library").hide()

    $("#create-schedule-entry").hide();
    $("#create-food-item").hide();

    $('#profile-tab-btn').removeClass('active')
    $('#meal-plan-tab-btn').removeClass('active')
    $('#library-tab-btn').removeClass('active')

    $('#profile-tab-btn').addClass('active')
})

$(document).on("click", "#meal-plan-tab-btn", function () {
    $("#profile").hide()
    $(".meal-plan-container").show()
    $("#library").hide()

    $("#create-schedule-entry").show();
    $("#create-food-item").hide();

    $('#profile-tab-btn').removeClass('active')
    $('#meal-plan-tab-btn').removeClass('active')
    $('#library-tab-btn').removeClass('active')

    $('#meal-plan-tab-btn').addClass('active')
})

$(document).on("click", "#library-tab-btn", function () {
    $("#profile").hide()
    $(".meal-plan-container").hide()
    $("#library").show()

    $("#create-schedule-entry").hide();
    $("#create-food-item").show();

    $('#profile-tab-btn').removeClass('active')
    $('#meal-plan-tab-btn').removeClass('active')
    $('#library-tab-btn').removeClass('active')

    $('#library-tab-btn').addClass('active')
})

$(document).on("click", "#create-food-item", function () {
    $(".modal-title").text("Add Food Item");
    $("#toggleFormSwitch").prop("checked", true);
    $("#toggleLabel").text("Add Ingredient");
    loadForm("piecemeal/food_item", { is_meal: true });
    $("#foodItemModal").modal("show");
});

$(document).on("click", "#create-schedule-entry", function () {
    $(".modal-title").text("Add Food Item");
    loadForm("piecemeal/schedule_entry", {});
    $(".modal-title").text("Add Schedule Entry");
    $("#foodItemModal").modal("show");
});

// When user toggles between forms
$(document).on("change", "#toggleFormSwitch", function () {
    if ($(this).is(":checked")) {
        $("#toggleLabel").text("Add Meal");
        loadForm("piecemeal/food_item", { is_meal: true });
    } else {
        $("#toggleLabel").text("Add Ingredient");
        loadForm("piecemeal/food_item", { is_meal: false });
    }
});

// Function to load form via AJAX
function loadForm(url, data) {
    $("#formContainer").empty();

    $.ajax({
        url: url + "/form/",
        type: "GET",
        data: data,
        success: function (data) {
            $("#formContainer").html(data);
            reloadIngredientNames();
            setupAutocomplete($(".entry-food-name-input"));
            setupAutocomplete($(".ingredient_name"));
        },
        error: function (xhr) {
            $("#formContainer").html(`${xhr.responseText}`);
        }
    });
}

// Handle form submissions
$(document).on("submit", ".create-food-item-form", function (e) {
    e.preventDefault();
    var form = this;
    var formType = $(form).data("type");
    var formData = $(form).serializeArray();
    formData.push({ name: "is_meal", value: formType === "meal" ? "true" : "false" });

    const isLibraryHidden = $("#library").is(":hidden");
    const isMealPlanHidden = $(".meal-plan-container").is(":hidden");

    $.ajax({
        url: form.action,
        type: form.method,
        data: $.param(formData),
        success: function (response) {
            if (response.success) {
                const day = response.day;
                $("#library").replaceWith(response.html_library);
                $(".meal-plan-container").replaceWith(response.html_meal_plan);
                $("#foodItemModal").modal("hide");
                if (isLibraryHidden) {
                    $("#library").hide();
                }
                if (isMealPlanHidden) {
                    $(".meal-plan-container").hide();
                }
                reloadIngredientNames();
                setupAutocomplete($(".entry-food-name-input"));
                setupAutocomplete($(".ingredient_name"));
            } else {
                // clear all invalids, so they don't accumulate
                $("input, select").removeClass("invalid");

                // set all invalid fields to be invalid
                response.field_errors.forEach(function (fieldName) {
                    $(`[name="${fieldName}"]`).addClass("invalid");
                });
            }
        },
        error: function (xhr) {
            $("#formContainer").html(xhr.responseText);
        }
    });
});

$(document).on("click", ".edit-food-item", function (e) {
    $(".modal-title").text("Edit Food Item");
    const food_item_id = $(this).data("id");
    $.ajax({
        url: "piecemeal/food_item/form/" + food_item_id + "/",
        type: "GET",
        success: function (data) {
            $("#formContainer").html(data);
            reloadIngredientNames();
            setupAutocomplete($(".entry-food-name-input"));
            setupAutocomplete($(".ingredient_name"));
            $("#foodItemModal").modal("show");
        }
    });
});

$(document).on("click", ".edit-schedule-entry", function (e) {
    $(".modal-title").text("Edit Schedule Entry");
    const entry_id = $(this).data("id");
    $.ajax({
        url: "piecemeal/schedule_entry/form/" + entry_id + "/",
        type: "GET",
        success: function (data) {
            $("#formContainer").html(data);
            reloadIngredientNames();
            setupAutocomplete($(".entry-food-name-input"));
            setupAutocomplete($(".ingredient_name"));
            $("#foodItemModal").modal("show");
        }
    });
});

$(document).on("submit", ".delete-food-item-form", function (e) {
    e.preventDefault();
    var form = $(this);

    const isLibraryHidden = $("#library").is(":hidden");
    const isMealPlanHidden = $(".meal-plan-container").is(":hidden");
    $.ajax({
        url: form.attr("action"),
        type: form.attr("method"),
        data: form.serialize(),
        success: function (response) {
            if (response.success) {
                $("#library").replaceWith(response.html_library);
                $(".meal-plan-container").replaceWith(response.html_meal_plan);
                reloadIngredientNames();
                setupAutocomplete($(".entry-food-name-input"));
                setupAutocomplete($(".ingredient_name"));
                if (isLibraryHidden) {
                    $("#library").hide();
                }
                if (isMealPlanHidden) {
                    $(".meal-plan-container").hide();
                }
            }
        },
        error: function (xhr) {
            alert("An error occurred removing the meal.");
        }
    });
});


$(document).on("submit", ".create-schedule-entry-form", function (e) {
    e.preventDefault();
    var form = this;

    const foodName = $(form).find(".entry-food-name-input").val();
    const quantity = $(form).find(".entry-quantity-input").val();
    const unit = $(document).find("select[name='ingredient_unit']").val();
    const days = [];
    $(form).find("input[name='days']:checked").each(function () {
        days.push($(this).val());
    });

    $.ajax({
        url: form.action,
        type: form.method,
        data: {
            name: foodName,
            quantity: quantity,
            unit: unit,
            days: days,
        },
        traditional: true, // important for arrays apparently 
        success: function (response) {
            if (response.success) {
                $(".meal-plan-container").replaceWith(response.html_meal_plan);
                reloadIngredientNames();
                setupAutocomplete($(".entry-food-name-input"));
                setupAutocomplete($(".ingredient_name"));
                $("#foodItemModal").modal("hide");
            } else {
                console.log(xhr.responseText);
            }
        },
        error: function (xhr) {
            $("#formContainer").html(xhr.responseText);
        }
    });
});

$(document).on("submit", ".delete-schedule-entry-form", function (e) {
    e.preventDefault();
    var form = $(this);
    $.ajax({
        url: form.attr("action"),
        type: form.attr("method"),
        data: form.serialize(),
        success: function (response) {
            if (response.success) {
                $(".meal-plan-container").replaceWith(response.html_meal_plan);
                reloadIngredientNames();
                setupAutocomplete($(".entry-food-name-input"));
                setupAutocomplete($(".ingredient_name"));
                $("#foodItemModal").modal("hide");
            }
        },
        error: function (xhr) {
            alert("An error occurred removing the meal.");
        }
    });
});

function updateMealMacros() {
    const ingredients = [];

    $("#ingredient-rows .ingredient-row").each(function () {
        const name = $(this).find(".ingredient-name").val();
        const quantity = $(this).find("input[name='ingredient_quantity']").val();
        const unit = $(this).find("select[name='ingredient_unit']").val();
        ingredients.push({ name: name, quantity: quantity, unit: unit });
    });

    $.ajax({
        url: "{% url 'calculate_macros' %}",
        type: "POST",
        data: JSON.stringify({ ingredients: ingredients }),
        contentType: "application/json",
        success: function (response) {
            if (response.success) {
                $("#ingredient-rows").replaceWith(response.html_meal_ingredients_list);
            }
        }
    });
}
$(document).on("blur", "#ingredient-rows input", updateMealMacros);
$(document).on("change", "#ingredient-rows input", updateMealMacros);
$(document).on("change", "#ingredient-rows select", updateMealMacros);

function update_schedule_entry_macros() {
    const form = $(this).closest("form");
    const name = form.find(".entry-food-name-input").val();
    const quantity = form.find(".entry-quantity-input").val();
    const unit = form.find("select[name='ingredient_unit']").val() ?? "servings";

    $.ajax({
        url: "{% url 'calculate_macros_schedule_item' %}",
        type: "POST",
        data: { name: name, quantity: quantity, unit: unit },
        success: function (response) {
            if (response.success) {
                $("#scheudle-entry-macros").replaceWith(response.html_macros);
                $("#scheudle-entry-units").replaceWith(response.html_units);
                console.log(response.html_units)
            }
        }
    });
}
$(document).on("blur", ".create-schedule-entry-form input", update_schedule_entry_macros);
$(document).on("change", ".create-schedule-entry-form input", update_schedule_entry_macros);
$(document).on("change", ".create-schedule-entry-form select", update_schedule_entry_macros);

$(document).on('input change', 'input.invalid, select.invalid, textarea.invalid', function () {
    $(this).removeClass('invalid');
});

// Meal ingredient row shit
var ingredientNames = [
    {% for ingredient in food_items %}
decodeHTMLEntities("{{ ingredient.name }}"),
    {% endfor %}
];

function reloadIngredientNames() {
    ingredientNames = [];
    $("#library .ingredient-name-autocomplete").each(function () {
        var encodedName = $(this).text().trim();
        var decodedName = decodeHTMLEntities(encodedName);
        if (decodedName && !ingredientNames.includes(decodedName)) {
            ingredientNames.push(decodedName);
        }
    });
}

function setupAutocomplete(input) {
    $(input).autocomplete({
        source: ingredientNames
    });
}

// Add new ingredient rows
$(document).on("click", "#add-ingredient-row", function () {
    var newRow = $(`
    {% include "piecemeal_app/partials/meal_ingredient_item.html" %}
    `);
    $("#ingredient-rows").append(newRow);
    setupAutocomplete(newRow.find(".ingredient-name"));
});
$(document).on("click", "#add-ingredient-row", updateMealMacros);

$(document).on("click", ".remove-row", function () {
    $(this).closest(".ingredient-row").remove();
});
$(document).on("click", ".remove-row", updateMealMacros);

// Initialize autocomplete for any initial rows
$(".ingredient-name").each(function () {
    setupAutocomplete(this);
});

$(document).on("click", ".kebab-toggle", function (e) {
    e.stopPropagation();
    $(".dropdown-menu").not($(this).siblings(".dropdown-menu")).hide(); // close any other dropdowns
    $(this).siblings(".dropdown-menu").toggle(); // toggle this one
});

$(document).on("click", function () {
    $(".dropdown-menu").hide();
});
