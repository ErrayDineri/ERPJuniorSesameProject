from django.urls import path
from .views import custom_login_view, signup_view, dashboard_view, logout_view, competence_list_view
from .views import exclusion_list_view, formation_list_view, abscence_list_view  # Import the new view
from django.urls import reverse_lazy

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard_view, name='dashboard'),
    path('competences/', competence_list_view, name='competence_list'),
    path('exclusions/', exclusion_list_view, name='exclusion_list'), 
    path('formation/', formation_list_view, name='formations'),
    path('abscence/', abscence_list_view, name='abscence'),# Add exclusions URL
]
