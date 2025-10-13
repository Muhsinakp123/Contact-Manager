from datetime import timedelta,datetime
from django.utils import timezone
from django.contrib import messages
from .forms import ResetPasswordForm
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

    # Fetch the first superuser (for demo display)
    admin_user = User.objects.filter(is_superuser=True).first()
    admin_username = admin_user.username if admin_user else "Not found"
    admin_password = "Muhsina@123"

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
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Invalid credentials',
                    'admin_username': admin_username,
                    'admin_password': admin_password
                })
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'admin_username': admin_username,
        'admin_password': admin_password
    })




# --- Forgot Password from login page ---
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()

        if not username:
            return render(request, 'login.html', {
                'form': LoginForm(),
                'error': 'Please enter your username first.'
            })

        try:
            user = User.objects.get(username=username)
            # Username found → redirect to reset password page
            return redirect('reset_password', user_id=user.id)

        except User.DoesNotExist:
            # Username invalid → show error *without redirecting*
            form = LoginForm(initial={'username': username})
            return render(request, 'login.html', {
                'form': form,
                'error': 'User not found. Please enter a valid username.'
            })


# --- Reset Password ---

def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    success_message = None  # message flag

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            # Show success message in same page instead of redirect
            success_message = "Password reset successfully! Redirecting to login..."
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {
        'form': form,
        'success_message': success_message
    })


# --- Dashboards ---
@login_required
def User_dashboard(request):
    contacts = Contact.objects.filter(owner=request.user)  # only this user's contacts
    return render(request, 'user dashboard/u_dashboard.html', {'contacts': contacts})

# --- Admin Views ---

@login_required
def admin_dashboard(request):
    # Count only non-superuser users
    total_users = User.objects.filter(is_superuser=False).count()

    # Total contacts
    total_contacts = Contact.objects.count()

    # ----- Calculate current week's Monday -----
    today = timezone.now().date()  # current date
    monday = today - timedelta(days=today.weekday())  # 0 = Monday, 6 = Sunday

    # Combine Monday's date with midnight time and make it timezone-aware
    monday_start = timezone.make_aware(datetime.combine(monday, datetime.min.time()))

    # Count users created this week (Monday → now)
    new_users_count = User.objects.filter(
        date_joined__gte=monday_start,
        is_superuser=False
    ).count()

    return render(request, 'admin dashboard/dashboard.html', {
        'total_users': total_users,
        'total_contacts': total_contacts,
        'new_users_count': new_users_count,
    })



@login_required
def admin_users(request):
    users = User.objects.filter(is_superuser=False)
    return render(request, 'admin dashboard/users_list.html', {'users': users})


@login_required
def admin_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'admin dashboard/contact_list.html', {'contacts': contacts})


@login_required
def delete_user(request, id):
    user = get_object_or_404(User, id=id)

    # If the logged-in user is deleting their own account
    if request.user == user:
        logout(request)  # log out first
        user.delete()    # then delete account
        return redirect('login')

    # If an admin deletes another user's account
    elif request.user.is_superuser:
        user.delete()
        return redirect('admin_users')

    else:
        # Unauthorized access protection
        return redirect('User_dashboard')

@login_required
def delete_contact_admin(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('admin_contacts')



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
    # Admin can update any contact; normal user only their own
    if request.user.is_superuser:
        contact = get_object_or_404(Contact, id=id)
    else:
        contact = get_object_or_404(Contact, id=id, owner=request.user)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            # Redirect based on who is logged in
            if request.user.is_superuser:
                return redirect('admin_contacts')
            else:
                return redirect('User_dashboard')
    else:
        form = ContactForm(instance=contact)
    if request.user.is_superuser:
        return render(request, 'user dashboard/update_contact.html', {'form': form})
    else:
        return render(request, 'user dashboard/update_contact.html', {'form': form})



@login_required
def update_user(request, id):
    # Admin can update any user; normal user only themselves
    if request.user.is_superuser:
        user_obj = get_object_or_404(User, id=id)
    else:
        if request.user.id != id:
            return redirect('User_dashboard')
        user_obj = request.user

    if request.method == 'POST':
        # Limit form fields to username and email only
        form = UserForm(request.POST, instance=user_obj)
        # Remove password fields from validation
        form.fields.pop('password', None)
        form.fields.pop('confirm_password', None)

        if form.is_valid():
            form.save()
            messages.success(request, "User details updated successfully!")
            if request.user.is_superuser:
                return redirect('admin_users')
            else:
                return redirect('User_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm(instance=user_obj)
        # Remove password fields from the rendered form
        form.fields.pop('password', None)
        form.fields.pop('confirm_password', None)

    return render(
        request,
        'admin dashboard/update_user.html',
        {'form': form, 'user_obj': user_obj}
    )



# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')

