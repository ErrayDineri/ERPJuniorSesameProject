from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.db import models

from .forms import CustomUserCreationForm, EmailAuthenticationForm
from .models import CustomUser, Absence, Formation, Performance, Competence, ExclusionDemission
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt

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
        # Get all user's records
        absences = Absence.objects.filter(membre=request.user)
        formations = Formation.objects.filter(membre=request.user)
        performances = Performance.objects.filter(membre=request.user)
        
        # Calculate dashboard statistics
        today = date.today()
        
        # Absences stats
        total_absences = absences.count()
        approved_absences = absences.filter(certificat_medical=True).count()
        absence_percentage = (approved_absences / total_absences * 100) if total_absences > 0 else 0
        
        # Formation stats
        total_formations = formations.count()
        active_formations = formations.filter(date_fin__gte=today).count()
        formation_percentage = (active_formations / total_formations * 100) if total_formations > 0 else 0
        
        # Performance stats
        latest_performance = performances.order_by('-date_evaluation').first()
        avg_performance = performances.aggregate(avg=models.Avg('note'))['avg'] or 0
        if latest_performance and latest_performance.note:
            perf_trend = latest_performance.note - avg_performance
        else:
            perf_trend = 0
            
        return render(request, 'user_dashboard.html', {
            'absences': absences,
            'formations': formations,
            'performances': performances,
            # Dashboard card stats
            'absence_count': total_absences,
            'absence_approved': approved_absences,
            'absence_percentage': int(absence_percentage),
            'formation_count': total_formations,
            'active_formations': active_formations,
            'formation_percentage': int(formation_percentage),
            'performance_score': round(avg_performance, 1) if avg_performance else 0,
            'performance_trend': round(perf_trend * 100, 1) if perf_trend else 0
        })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def competence_list_view(request):
    user = request.user
    edit_id = None
    # Annuler édition
    if request.method == 'GET' and 'cancel' in request.GET:
        return redirect('competence_list')
    # Suppression d'une compétence
    if request.method == 'POST' and 'delete' in request.GET:
        comp_id = request.GET.get('delete')
        Competence.objects.filter(id=comp_id, formation__membre=user).delete()
        return redirect('competence_list')
    # Début édition (affichage champ modifiable)
    if request.method == 'POST' and 'edit' in request.GET:
        edit_id = int(request.GET.get('edit'))
    # Enregistrement modification
    if request.method == 'POST' and 'edit' in request.GET and 'new_libelle' in request.POST:
        comp_id = int(request.GET.get('edit'))
        new_libelle = request.POST.get('new_libelle')
        Competence.objects.filter(id=comp_id, formation__membre=user).update(libelle=new_libelle)
        return redirect('competence_list')
    # Ajout d'une compétence
    if request.method == 'POST' and not ('delete' in request.GET or 'edit' in request.GET):
        competence_libelle = request.POST.get('competence')
        categorie = request.POST.get('categorie')
        if competence_libelle and categorie:
            formation, _ = Formation.objects.get_or_create(
                membre=user, intitule='Générique',
                defaults={'organisme': 'Club', 'date_debut': '2025-01-01', 'date_fin': '2025-12-31', 'certification': False}
            )
            Competence.objects.create(
                formation=formation, code=competence_libelle[:10], libelle=competence_libelle, categorie=categorie
            )
        return redirect('competence_list')
    # Préparer les compétences de l'utilisateur connecté
    formations = Formation.objects.filter(membre=user)
    competences = Competence.objects.filter(formation__in=formations)
    hard_skills = [c for c in competences if c.categorie == 'Hard']
    soft_skills = [c for c in competences if c.categorie == 'Soft']
    return render(request, 'Competence_list.html', {
        'hard_skills': hard_skills,
        'soft_skills': soft_skills,
        'edit_id': edit_id
    })

@login_required
def exclusion_list_view(request):
    from .models import CustomUser
    exclusions = ExclusionDemission.objects.all()
    members = CustomUser.objects.all()
    today = date.today()
    # Handle delete
    if request.method == 'POST' and 'delete_id' in request.POST:
        delete_id = request.POST.get('delete_id')
        ExclusionDemission.objects.filter(id=delete_id).delete()
        return redirect('exclusion_list')
    # Handle edit
    if request.method == 'POST' and 'edit_id' in request.POST:
        edit_id = request.POST.get('edit_id')
        exclusion = ExclusionDemission.objects.get(id=edit_id)
        membre_id = request.POST.get('membre')
        motif = request.POST.get('motif')
        type_ = request.POST.get('type')
        date_effet = request.POST.get('date_effet')
        document_reference = request.POST.get('document_reference')
        if membre_id and motif and type_ and date_effet:
            exclusion.membre = CustomUser.objects.get(id=membre_id)
            exclusion.motif = motif
            exclusion.type = type_
            exclusion.date_effet = date_effet
            exclusion.document_reference = document_reference or ''
            exclusion.save()
        return redirect('exclusion_list')
    # Handle add
    if request.method == 'POST' and 'membre' in request.POST and 'edit_id' not in request.POST:
        membre_id = request.POST.get('membre')
        motif = request.POST.get('motif')
        type_ = request.POST.get('type')
        date_effet = request.POST.get('date_effet')
        document_reference = request.POST.get('document_reference')
        if membre_id and motif and type_ and date_effet:
            membre = CustomUser.objects.get(id=membre_id)
            ExclusionDemission.objects.create(
                membre=membre,
                motif=motif,
                type=type_,
                date_effet=date_effet,
                document_reference=document_reference or ''
            )
        return redirect('exclusion_list')
    return render(request, 'Exclusion_list.html', {'exclusions': exclusions, 'members': members, 'today': today})

@login_required
def formation_list_view(request):
    formations = Formation.objects.filter(membre=request.user)
    return render(request, 'formations.html', {'formations': formations})

@login_required
def abscence_list_view(request):
    absences = Absence.objects.filter(membre=request.user)
    return render(request, 'abscence.html', {'absences': absences})
