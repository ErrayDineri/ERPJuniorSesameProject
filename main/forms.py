from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


UserModel = get_user_model()

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct email and password."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user_obj = UserModel.objects.get(email__iexact=email)
            except UserModel.DoesNotExist:
                user_obj = None
            if user_obj:
                self.user_cache = authenticate(self.request,username=user_obj.username,password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                if not self.user_cache.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse_postale', 'date_adhesion']
        widgets = {
            'date_adhesion': forms.DateInput(attrs={'type': 'date'}),
            'adresse_postale': forms.Textarea(attrs={'rows': 3}),
        }