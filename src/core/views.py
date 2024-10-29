from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.urls import reverse_lazy
from . forms import CustomAuthenticationForm, UserRegisterForm
from django.views.generic import CreateView, View
from core.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'core/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('landing_page')
    

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('core:login')
    
    def form_valid(self, form):
        user = form.save()
        
        # Create user profile
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        UserProfile.objects.create(
            user=user, 
            first_name=first_name, 
            last_name=last_name, 
            is_central_admin=True
            )

        login(self.request, user)
        return redirect('landing_page')
    
