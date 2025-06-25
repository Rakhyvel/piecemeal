from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from .models import UserCounter

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log them in automatically
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'piecemeal_app/signup.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    counter, _ = UserCounter.objects.get_or_create(user=request.user)
    return render(request, 'piecemeal_app/home.html', {'counter': counter})

@login_required
def increment_counter(request):
    counter, _ = UserCounter.objects.get_or_create(user=request.user)
    counter.count += 1
    print(counter.count)
    counter.save()
    return redirect('home')