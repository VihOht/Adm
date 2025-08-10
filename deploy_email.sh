#!/bin/bash

# =============================================================================
# Production Deployment Script for VihOhtLife
# =============================================================================

echo "🚀 VihOhtLife Production Deployment"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Function to set Railway environment variable
set_railway_var() {
    local var_name="$1"
    local var_value="$2"
    echo "Setting $var_name..."
    railway variables set "$var_name=$var_value"
}

echo ""
echo "📧 Email Configuration Setup"
echo "----------------------------"

# Prompt for email provider choice
echo "Choose your email provider:"
echo "1) Gmail (Personal/Development)"
echo "2) SendGrid (Production Recommended)"
echo "3) Mailgun (Alternative Production)"
echo "4) Custom SMTP"

read -p "Enter your choice (1-4): " email_choice

case $email_choice in
    1)
        echo ""
        echo "📧 Gmail Configuration"
        echo "--------------------"
        echo "Before proceeding, make sure you have:"
        echo "1. Enabled 2-Factor Authentication on Gmail"
        echo "2. Generated an App Password"
        echo ""
        
        read -p "Enter your Gmail address: " gmail_address
        read -s -p "Enter your Gmail App Password (16 characters): " gmail_password
        echo ""
        
        set_railway_var "EMAIL_HOST" "smtp.gmail.com"
        set_railway_var "EMAIL_PORT" "587"
        set_railway_var "EMAIL_USE_TLS" "true"
        set_railway_var "EMAIL_USE_SSL" "false"
        set_railway_var "EMAIL_HOST_USER" "$gmail_address"
        set_railway_var "EMAIL_HOST_PASSWORD" "$gmail_password"
        set_railway_var "DEFAULT_FROM_EMAIL" "VihOhtLife <$gmail_address>"
        set_railway_var "SERVER_EMAIL" "VihOhtLife <$gmail_address>"
        ;;
        
    2)
        echo ""
        echo "📧 SendGrid Configuration"
        echo "------------------------"
        echo "Before proceeding, make sure you have:"
        echo "1. Created a SendGrid account"
        echo "2. Generated an API key with Mail Send permissions"
        echo "3. Verified your sender email/domain"
        echo ""
        
        read -p "Enter your SendGrid API key: " sendgrid_key
        read -p "Enter your 'from' email address: " from_email
        
        set_railway_var "EMAIL_HOST" "smtp.sendgrid.net"
        set_railway_var "EMAIL_PORT" "587"
        set_railway_var "EMAIL_USE_TLS" "true"
        set_railway_var "EMAIL_USE_SSL" "false"
        set_railway_var "EMAIL_HOST_USER" "apikey"
        set_railway_var "EMAIL_HOST_PASSWORD" "$sendgrid_key"
        set_railway_var "DEFAULT_FROM_EMAIL" "VihOhtLife <$from_email>"
        set_railway_var "SERVER_EMAIL" "VihOhtLife <$from_email>"
        ;;
        
    3)
        echo ""
        echo "📧 Mailgun Configuration"
        echo "-----------------------"
        echo "Before proceeding, make sure you have:"
        echo "1. Created a Mailgun account"
        echo "2. Added and verified your domain"
        echo "3. Obtained SMTP credentials"
        echo ""
        
        read -p "Enter your Mailgun domain (e.g., mg.yourdomain.com): " mailgun_domain
        read -p "Enter your Mailgun SMTP username: " mailgun_user
        read -s -p "Enter your Mailgun SMTP password: " mailgun_password
        echo ""
        read -p "Enter your 'from' email address: " from_email
        
        set_railway_var "EMAIL_HOST" "smtp.mailgun.org"
        set_railway_var "EMAIL_PORT" "587"
        set_railway_var "EMAIL_USE_TLS" "true"
        set_railway_var "EMAIL_USE_SSL" "false"
        set_railway_var "EMAIL_HOST_USER" "$mailgun_user"
        set_railway_var "EMAIL_HOST_PASSWORD" "$mailgun_password"
        set_railway_var "DEFAULT_FROM_EMAIL" "VihOhtLife <$from_email>"
        set_railway_var "SERVER_EMAIL" "VihOhtLife <$from_email>"
        ;;
        
    4)
        echo ""
        echo "📧 Custom SMTP Configuration"
        echo "---------------------------"
        
        read -p "Enter SMTP host: " smtp_host
        read -p "Enter SMTP port (usually 587 or 465): " smtp_port
        read -p "Use TLS? (true/false): " use_tls
        read -p "Use SSL? (true/false): " use_ssl
        read -p "Enter SMTP username: " smtp_user
        read -s -p "Enter SMTP password: " smtp_password
        echo ""
        read -p "Enter your 'from' email address: " from_email
        
        set_railway_var "EMAIL_HOST" "$smtp_host"
        set_railway_var "EMAIL_PORT" "$smtp_port"
        set_railway_var "EMAIL_USE_TLS" "$use_tls"
        set_railway_var "EMAIL_USE_SSL" "$use_ssl"
        set_railway_var "EMAIL_HOST_USER" "$smtp_user"
        set_railway_var "EMAIL_HOST_PASSWORD" "$smtp_password"
        set_railway_var "DEFAULT_FROM_EMAIL" "VihOhtLife <$from_email>"
        set_railway_var "SERVER_EMAIL" "VihOhtLife <$from_email>"
        ;;
        
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🔐 Security Configuration"
echo "------------------------"

# Set additional email and security settings
set_railway_var "EMAIL_BACKEND" "django.core.mail.backends.smtp.EmailBackend"
set_railway_var "EMAIL_TIMEOUT" "30"
set_railway_var "PASSWORD_RESET_TIMEOUT" "259200"
set_railway_var "SECURE_SSL_REDIRECT" "true"

echo ""
echo "🎯 Final Steps"
echo "-------------"

echo "1. Deploy your application:"
echo "   railway up"
echo ""
echo "2. Run migrations:"
echo "   railway run python manage.py migrate"
echo ""
echo "3. Create superuser:"
echo "   railway run python manage.py createsuperuser"
echo ""
echo "4. Create default categories for users:"
echo "   railway run python manage.py create_default_categories"
echo ""
echo "5. Test email configuration:"
echo "   railway run python manage.py test_email --to your-email@example.com"
echo ""

echo "✅ Email configuration completed!"
echo ""
echo "📋 Quick Test Commands:"
echo "railway run python manage.py test_email --to your-email@example.com"
echo "railway run python manage.py test_email --to your-email@example.com --test-password-reset"
echo ""
echo "🔗 Useful Links:"
echo "- Railway Dashboard: https://railway.app/dashboard"
echo "- Your App URL: https://vihohtlife.up.railway.app"
echo ""
echo "📞 Need Help?"
echo "Check the EMAIL_SETUP_GUIDE.md file for detailed instructions."
