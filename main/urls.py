from django.urls import path
from .views import custom_login_view, signup_view, dashboard_view, logout_view
from django.urls import reverse_lazy

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard_view, name='dashboard'),
]
