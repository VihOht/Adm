from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User


def login_view(request):
    """Login view for authentication"""
    if request.user.is_authenticated:
        return redirect("landingpage")

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


def register_view(request):
    """Register new user view"""
    if request.user.is_authenticated:
        return redirect("landingpage:index")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        accept_terms = request.POST.get("accept_terms")

        # Basic validation
        if not all([username, email, password1, password2]):
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            return render(request, "authentication/register.html")

        if not accept_terms:
            messages.error(request, "Você deve aceitar os termos e condições.")
            return render(request, "authentication/register.html")

        if password1 != password2:
            messages.error(request, "As senhas não conferem.")
            return render(request, "authentication/register.html")

        if len(password1) < 8:
            messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
            return render(request, "authentication/register.html")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já existe.")
            return render(request, "authentication/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email já está cadastrado.")
            return render(request, "authentication/register.html")

        try:
            # Create user
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name or "",
                    last_name=last_name or "",
                )

            messages.success(
                request,
                f"Conta criada com sucesso para {user.username}! Você pode fazer login agora.",
            )
            return redirect("authentication:login")

        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return render(request, "authentication/register.html")

    return render(request, "authentication/register.html")


def password_reset_view(request):
    """Password reset request view"""
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Por favor, digite seu email.")
            return render(request, "authentication/password_reset_form.html")

        try:
            user = User.objects.get(email=email)

            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create reset link
            reset_link = request.build_absolute_uri(
                reverse(
                    "authentication:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
            )

            # Email context
            context = {
                "email": user.email,
                "domain": request.get_host(),
                "site_name": "VihOhtLife",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": "https" if request.is_secure() else "http",
            }

            # Render email templates
            subject = render_to_string(
                "registration/password_reset_subject.txt", context
            )
            subject = "".join(subject.splitlines())  # Remove newlines

            body = render_to_string("registration/password_reset_email.txt", context)

            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Email de recuperação enviado com sucesso!")
            except Exception as e:
                # If email fails, still redirect but show the link in messages for development
                print(f"Email error: {e}")
                print(f"Password reset link: {reset_link}")  # For development
                messages.warning(
                    request,
                    "Email não pôde ser enviado. Verifique a configuração do servidor de email.",
                )
                messages.info(
                    request, f"Link de recuperação (desenvolvimento): {reset_link}"
                )

            return redirect("authentication:password_reset_done")

        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(
                request,
                "Se o email existir em nosso sistema, você receberá um link de recuperação.",
            )
            return redirect("authentication:password_reset_done")

    return render(request, "authentication/password_reset_form.html")


def password_reset_done_view(request):
    """Password reset done view"""
    return render(request, "authentication/password_reset_done.html")


def password_reset_confirm_view(request, uidb64, token):
    """Password reset confirm view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")

            if not all([new_password1, new_password2]):
                messages.error(request, "Por favor, preencha todos os campos.")
                return render(request, "authentication/password_reset_confirm.html")

            if new_password1 != new_password2:
                messages.error(request, "As senhas não conferem.")
                return render(request, "authentication/password_reset_confirm.html")

            if len(new_password1) < 8:
                messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
                return render(request, "authentication/password_reset_confirm.html")

            # Set new password
            user.set_password(new_password1)
            user.save()

            messages.success(request, "Senha alterada com sucesso!")
            return redirect("authentication:password_reset_complete")

        return render(request, "authentication/password_reset_confirm.html")
    else:
        messages.error(request, "Link de recuperação inválido ou expirado.")
        return redirect("authentication:password_reset")


def password_reset_complete_view(request):
    """Password reset complete view"""
    return render(request, "authentication/password_reset_complete.html")
