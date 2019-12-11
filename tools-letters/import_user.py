"""
Usage:

/app/tools-letters # python tools-letters/import_user.py

"""
import os
import django
import sys
import csv
sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()
from django.db import transaction
from account.models import User, UserProfile, AdminType
from django.contrib.auth.hashers import make_password



def create_if_not_exists(username, 
                         email,
                         password,
                         admin_type=AdminType.REGULAR_USER,
                         real_name=None):
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        with transaction.atomic():
            ins, created = User.objects.get_or_create(
                username=username,
                email=email,
                password=make_password(password),
                admin_type=admin_type,
            )
            ins, created = UserProfile.objects.get_or_create(
                user=ins,
                real_name=real_name
            )


create_if_not_exists(
    username='LETTers',
    email='LETTers@letters.cn',
    password='letters@519',
    admin_type=AdminType.ADMIN
)

with open('2019-users-with-pwd.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        student_id, real_name, _, _, _, email, password = row
        create_if_not_exists(
            username=student_id,
            email=email,
            password=password,
            real_name=real_name
        )

