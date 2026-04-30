from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Automatically create admin user if it does not exist"

    def handle(self, *args, **kwargs):
        username = os.environ.get("gfigueroa07")
        email = os.environ.get("guillermofigueroa2840@gmail.com")
        password = os.environ.get("Snoopylana7!")

        if not username or not password:
            self.stdout.write("Missing admin env vars")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin already exists")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write("Admin user created successfully")