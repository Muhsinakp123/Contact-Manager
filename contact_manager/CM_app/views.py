from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserForm
from .models import Profile

# --- Register ---
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.save()

            return redirect('login')
    else:
        form = UserForm()

    return render(request, 'signup.html', {'form': form})


# --- Login ---
def login_View(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('User_dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# --- Dashboards ---
@login_required
def User_dashboard(request):
    return render(request, 'user dashboard/u_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin dashboard/dashboard.html')


# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

