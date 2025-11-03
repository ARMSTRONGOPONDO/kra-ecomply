import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomply.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create Admin Superuser
admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@ecomply.com')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=admin_username).exists():
    User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
    print(f'✅ Admin user created: username="{admin_username}", password="{admin_password}"')
else:
    print(f'ℹ️  Admin user "{admin_username}" already exists.')

# Create Regular User
user_username = os.environ.get('DJANGO_USER_USERNAME', 'user')
user_email = os.environ.get('DJANGO_USER_EMAIL', 'user@ecomply.com')
user_password = os.environ.get('DJANGO_USER_PASSWORD', 'user')

if not User.objects.filter(username=user_username).exists():
    User.objects.create_user(username=user_username, email=user_email, password=user_password)
    print(f'✅ Regular user created: username="{user_username}", password="{user_password}"')
else:
    print(f'ℹ️  Regular user "{user_username}" already exists.')

print('\n📝 Login Credentials:')
print(f'Admin: {admin_username} / {admin_password}')
print(f'User:  {user_username} / {user_password}')
