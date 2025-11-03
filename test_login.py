#!/usr/bin/env python3
"""Test script to verify user creation locally"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomply.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

print("=== Testing User Authentication ===\n")

# Check if users exist
admin_exists = User.objects.filter(username='admin').exists()
user_exists = User.objects.filter(username='user').exists()

print(f"Admin user exists: {admin_exists}")
print(f"Regular user exists: {user_exists}")

# Try to authenticate
print("\n=== Testing Login ===")

admin_auth = authenticate(username='admin', password='admin')
print(f"Admin login (admin/admin): {'✅ SUCCESS' if admin_auth else '❌ FAILED'}")

user_auth = authenticate(username='user', password='user')
print(f"User login (user/user): {'✅ SUCCESS' if user_auth else '❌ FAILED'}")

# List all users
print("\n=== All Users in Database ===")
for u in User.objects.all():
    print(f"- {u.username} (is_superuser: {u.is_superuser}, is_staff: {u.is_staff})")
