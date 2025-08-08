from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def login_view(request):
    """Login view for authentication"""
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "landingpage")
                messages.success(request, "Login Realizado com Sucesso")
                messages.success(request, f"Bem Vindo {user.username}")
                return redirect(next_url)
            else:
                messages.error(request, "Email ou senha inválidos.")
        else:
            messages.error(request, "Por favor, preencha todos os campos.")

    return render(request, "authentication/login.html")


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, "Logout realizado com sucesso.")
    return redirect("authentication:login")


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, "authentication/profile.html")
