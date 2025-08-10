from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from finance_manager.models import ExpenseCategory, IncomeCategorys

User = get_user_model()


class Command(BaseCommand):
    help = "Create default categories for users who don't have any"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="Create categories for specific user (by username or email)",
        )

    def handle(self, *args, **options):
        default_expense_categories = [
            {
                "name": "Alimentação",
                "description": "Gastos com comida e bebida",
                "color": "#FF6B6B",
            },
            {
                "name": "Transporte",
                "description": "Gastos com transporte público, combustível, etc.",
                "color": "#4ECDC4",
            },
            {
                "name": "Moradia",
                "description": "Aluguel, financiamento, contas da casa",
                "color": "#45B7D1",
            },
            {
                "name": "Saúde",
                "description": "Médicos, medicamentos, plano de saúde",
                "color": "#96CEB4",
            },
            {
                "name": "Lazer",
                "description": "Cinema, shows, viagens, hobbies",
                "color": "#FECA57",
            },
            {
                "name": "Educação",
                "description": "Cursos, livros, material escolar",
                "color": "#6C5CE7",
            },
            {"name": "Outros", "description": "Gastos diversos", "color": "#A0A0A0"},
        ]

        default_income_categories = [
            {
                "name": "Salário",
                "description": "Renda do trabalho principal",
                "color": "#00B894",
            },
            {
                "name": "Freelance",
                "description": "Trabalhos extras e projetos",
                "color": "#00CEC9",
            },
            {
                "name": "Investimentos",
                "description": "Rendimentos de aplicações",
                "color": "#6C5CE7",
            },
            {
                "name": "Vendas",
                "description": "Vendas de produtos ou serviços",
                "color": "#E17055",
            },
            {
                "name": "Outros",
                "description": "Outras fontes de renda",
                "color": "#74B9FF",
            },
        ]

        if options["user"]:
            # Create categories for specific user
            try:
                user = User.objects.get(username=options["user"])
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=options["user"])
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'User "{options["user"]}" not found')
                    )
                    return

            users_to_process = [user]
        else:
            # Create categories for all users who don't have any
            users_to_process = User.objects.all()

        for user in users_to_process:
            # Check if user already has categories
            expense_count = ExpenseCategory.objects.filter(user=user).count()
            income_count = IncomeCategorys.objects.filter(user=user).count()

            if expense_count == 0:
                self.stdout.write(f"Creating expense categories for {user.username}...")
                for cat_data in default_expense_categories:
                    category, created = ExpenseCategory.objects.get_or_create(
                        user=user,
                        name=cat_data["name"],
                        defaults={
                            "description": cat_data["description"],
                            "color": cat_data["color"],
                        },
                    )
                    if created:
                        self.stdout.write(f"  ✓ Created: {category.name}")

            if income_count == 0:
                self.stdout.write(f"Creating income categories for {user.username}...")
                for cat_data in default_income_categories:
                    category, created = IncomeCategorys.objects.get_or_create(
                        user=user,
                        name=cat_data["name"],
                        defaults={
                            "description": cat_data["description"],
                            "color": cat_data["color"],
                        },
                    )
                    if created:
                        self.stdout.write(f"  ✓ Created: {category.name}")

        self.stdout.write(self.style.SUCCESS("Successfully created default categories"))
