from django.urls import path
from . import views

urlpatterns = [
    # --- ACCUEIL ET PANIER ---
    path('', views.index, name='index'), # Nom principal (utilisé pour les redirections)
    path('accueil/', views.index, name='liste_produits'), # Surnom de sécurité
    path('panier/', views.voir_panier, name='voir_panier'),
    path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/supprimer/<int:produit_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('commander/', views.commander, name='commander'),

    # --- ESPACE AGRICULTEUR (DASHBOARD) ---
    path('inscription/', views.inscription_agriculteur, name='inscription'),
    path('mon-espace/', views.dashboard_agri, name='dashboard_agri'),
    path('ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('modifier-produit/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('supprimer-produit/<int:pk>/', views.supprimer_produit, name='supprimer_produit'),
    
    # --- GESTION DES COMMANDES ---
    path('valider-commande/<int:commande_id>/', views.valider_commande, name='valider_commande'),
    path('annuler-commande/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
    path('facture/<int:commande_id>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    
    # --- PROFIL ---
    path('mon-profil/', views.mon_profil, name='mon_profil'),
    path('chatbot-api/', views.chatbot_logic, name='chatbot_api'),
]