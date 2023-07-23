from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from .forms import LoginForm


# Create your views here.


class LoginView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'accounts/login.html')

    def post(self, request: HttpRequest) -> HttpResponse:
        redirect_url: str = request.GET.get('next')

        form = LoginForm(data=request.POST)

        if form.is_valid():
            login_with: str = form.cleaned_data.get('login_with')
            password: str = form.cleaned_data.get('password')

            # Note: we are using the default django authenticate function, so username argument is passed
            user = authenticate(username=login_with, password=password)
            if user:
                login(request, user)
                return redirect(redirect_url if redirect_url else '/')

            login_with_method = get_user_model().login_method().title()
            form.add_error('password', f'{login_with_method} or password don\'t match')

        return render(request, 'accounts/login.html', {
            'form': form
        })


class LogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect(settings.LOGIN_URL)
