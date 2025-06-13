from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm, EmailAuthenticationForm
from .models import CustomUser, Absence, Formation, Performance
from django.contrib.auth.models import Group

def custom_login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailAuthenticationForm(request)
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group, _ = Group.objects.get_or_create(name='Membre')
            user.groups.add(group)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

@login_required
def dashboard_view(request):
    if is_admin(request.user):
        membres = CustomUser.objects.all()
        return render(request, 'admin_dashboard.html', {'membres': membres})
    else:
        absences     = Absence.objects.filter(membre=request.user)
        formations   = Formation.objects.filter(membre=request.user)
        performances = Performance.objects.filter(membre=request.user)
        return render(request, 'user_dashboard.html', {
            'absences': absences,
            'formations': formations,
            'performances': performances,
        })

def logout_view(request):
    logout(request)
    return redirect('login')
