import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    username = 'admin'
    password = 'admin'
    email = 'admin@example.com'
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username, email, password)
    else:
        print(f"User {username} already exists")

if __name__ == '__main__':
    create_admin()
