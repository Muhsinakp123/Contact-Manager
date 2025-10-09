from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, UserForm
from .models import Contact
from .forms import ContactForm
from django.contrib.auth.models import User

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
    contacts = Contact.objects.filter(owner=request.user)  # only this user's contacts
    return render(request, 'user dashboard/u_dashboard.html', {'contacts': contacts})

@login_required
def admin_dashboard(request):
    return render(request, 'admin dashboard/dashboard.html')

@login_required
def admin_users(request):
    return render(request, 'admin dashboard/users_list.html')

@login_required
def admin_contacts(request):
    return render(request, 'admin dashboard/contact_list.html')

@login_required
def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user  # assign logged-in user as owner
            contact.save()
            return redirect('User_dashboard')
    else:
        form = ContactForm()
    
    return render(request, 'user dashboard/add_contact.html', {'form': form})

@login_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id, owner=request.user)  # ensure only owner can delete
    contact.delete()
    return redirect('User_dashboard')

@login_required
def update_contact(request, id):
    contact = get_object_or_404(Contact, id=id, owner=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('User_dashboard')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'user dashboard/update_contact.html', {'form': form})




# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

