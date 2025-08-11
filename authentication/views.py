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


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "upload_photo":
            # Handle profile image upload
            if "profile_image" in request.FILES:
                profile_image = request.FILES["profile_image"]

                # Validate file size (5MB max)
                if profile_image.size > 5 * 1024 * 1024:
                    messages.error(request, "A imagem deve ter no máximo 5MB.")
                    return render(request, "authentication/edit_profile.html")

                # Validate file type
                allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
                if profile_image.content_type not in allowed_types:
                    messages.error(
                        request, "Apenas imagens JPG, PNG e WEBP são permitidas."
                    )
                    return render(request, "authentication/edit_profile.html")

                try:
                    # Delete old image if exists
                    if request.user.profile_image:
                        request.user.delete_profile_image()

                    request.user.profile_image = profile_image
                    request.user.save()
                    messages.success(request, "Foto de perfil atualizada com sucesso!")

                except Exception as e:
                    messages.error(request, f"Erro ao atualizar foto: {str(e)}")

            else:
                messages.error(request, "Nenhuma imagem foi selecionada.")

        elif action == "delete_photo":
            # Handle photo deletion
            try:
                request.user.delete_profile_image()
                messages.success(request, "Foto de perfil removida com sucesso!")
            except Exception as e:
                messages.error(request, f"Erro ao remover foto: {str(e)}")

        elif action == "update_profile":
            # Handle profile information update
            username = request.POST.get("username", "").strip()

            # Validation
            if not username:
                messages.error(request, "Nome de usuário é obrigatório.")
                return render(request, "authentication/edit_profile.html")

            # Check if username is taken by another user
            if (
                User.objects.filter(username=username)
                .exclude(id=request.user.id)
                .exists()
            ):
                messages.error(request, "Este nome de usuário já está em uso.")
                return render(request, "authentication/edit_profile.html")

            try:
                # Update user information
                request.user.username = username
                request.user.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect("authentication:profile")

            except Exception as e:
                messages.error(request, f"Erro ao atualizar perfil: {str(e)}")

    return render(request, "authentication/edit_profile.html")


@login_required
def change_password_view(request):
    """Change user password view"""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        # Validation
        if not all([current_password, new_password1, new_password2]):
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "authentication/change_password.html")

        # Check current password
        if not request.user.check_password(current_password):
            messages.error(request, "Senha atual incorreta.")
            return render(request, "authentication/change_password.html")

        # Check if new passwords match
        if new_password1 != new_password2:
            messages.error(request, "As novas senhas não conferem.")
            return render(request, "authentication/change_password.html")

        # Check password strength
        if len(new_password1) < 8:
            messages.error(request, "A nova senha deve ter pelo menos 8 caracteres.")
            return render(request, "authentication/change_password.html")

        # Check if new password is different from current
        if request.user.check_password(new_password1):
            messages.error(request, "A nova senha deve ser diferente da senha atual.")
            return render(request, "authentication/change_password.html")

        try:
            # Update password
            request.user.set_password(new_password1)
            request.user.save()

            # Re-authenticate user to maintain session
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, request.user)

            messages.success(request, "Senha alterada com sucesso!")
            return redirect("authentication:profile")

        except Exception as e:
            messages.error(request, f"Erro ao alterar senha: {str(e)}")
            return render(request, "authentication/change_password.html")

    return render(request, "authentication/change_password.html")


@login_required
def delete_profile_image_view(request):
    """Delete user profile image"""
    if request.method == "POST":
        try:
            request.user.delete_profile_image()
            messages.success(request, "Foto de perfil removida com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao remover foto: {str(e)}")

    return redirect("authentication:edit_profile")


def register_view(request):
    """Register new user view"""
    if request.user.is_authenticated:
        return redirect("landingpage:index")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
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

            # Email context with proper domain handling
            domain = request.get_host()
            # Handle Railway.app subdomain properly
            if "railway.app" in domain:
                protocol = "https"
            else:
                protocol = "https" if request.is_secure() else "http"

            context = {
                "email": user.email,
                "domain": domain,
                "site_name": "VihOhtLife",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": protocol,
                "reset_url": reset_link,
            }

            # Render email templates
            subject = render_to_string(
                "registration/password_reset_subject.txt", context
            )
            subject = "".join(subject.splitlines())  # Remove newlines

            body = render_to_string("registration/password_reset_email.txt", context)

            try:
                # Validate email configuration
                if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                    messages.error(
                        request,
                        "Serviço de email não configurado. Entre em contato com o administrador.",
                    )
                    return render(request, "authentication/password_reset_form.html")

                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Email de recuperação enviado com sucesso!")

            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Email sending failed: {e}")

                # More detailed error handling for production
                if settings.DEBUG:
                    messages.error(request, f"Erro ao enviar email: {str(e)}")
                else:
                    messages.warning(
                        request,
                        "Não foi possível enviar o email de recuperação. Tente novamente em alguns minutos.",
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
