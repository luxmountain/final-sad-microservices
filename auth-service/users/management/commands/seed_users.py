from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo sẵn tài khoản admin, manager, customer để test'

    def handle(self, *args, **options):
        accounts = [
            {'username': 'admin',    'password': 'admin123',    'role': 'staff',    'email': 'admin@lumiere.vn'},
            {'username': 'manager',  'password': 'manager123',  'role': 'manager',  'email': 'manager@lumiere.vn'},
            {'username': 'customer', 'password': 'customer123', 'role': 'customer', 'email': 'customer@lumiere.vn'},
        ]

        for acc in accounts:
            if not User.objects.filter(username=acc['username']).exists():
                User.objects.create_user(
                    username=acc['username'],
                    password=acc['password'],
                    email=acc['email'],
                    role=acc['role'],
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Tạo user '{acc['username']}' (role={acc['role']})"))
            else:
                self.stdout.write(self.style.WARNING(f"⏭️  User '{acc['username']}' đã tồn tại, bỏ qua."))
