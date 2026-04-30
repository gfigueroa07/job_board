from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Auto create admin user"

    def handle(self, *args, **kwargs):
        username = "admin"
        email = "admin@example.com"
        password = "admin12345"

        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin already exists")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write("Admin created successfully")