import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Passe123')
    print("Succès : Compte admin créé !")
else:
    # Si l'utilisateur existe mais que tu as oublié le mot de passe
    user = User.objects.get(username='admin')
    user.set_password('Passe123')
    user.save()
    print("Succès : Mot de passe réinitialisé !")