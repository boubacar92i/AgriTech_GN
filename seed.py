import os
import sys
import django

# Détection automatique du dossier racine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Connexion Django réussie !")
except Exception as e:
    print(f"❌ Erreur : {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from marche.models import Produit, Profile

def run_seed():
    print("--- 🛒 Insertion des produits AgriTech ---")
    
    # Création Agriculteur
    user, _ = User.objects.get_or_create(username="Agri_Test")
    user.set_password("pass123")
    user.save()
    
    # Rôle AGRI
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.role = 'AGRI'
    profile.save()

    # Données
    produits = [
        {"nom": "Mangue Kent", "prix": 15000, "stock": 50},
        {"nom": "Riz étuvé", "prix": 180000, "stock": 10},
        {"nom": "Ananas Pain de Sucre", "prix": 10000, "stock": 5},
    ]

    for p in produits:
        Produit.objects.update_or_create(
            nom=p["nom"], vendeur=user,
            defaults={'prix': p["prix"], 'quantite_stock': p["stock"]}
        )
        print(f"📦 Produit prêt : {p['nom']}")

    print("--- ✨ Terminé ! ---")

if __name__ == "__main__":
    run_seed()