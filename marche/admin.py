from django.contrib import admin
from .models import Categorie, Produit, Commande, LigneCommande
from .models import Profile

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    # On affiche les champs qui existent REELLEMENT dans ton modèle Produit
    list_display = ('nom', 'zone_production', 'prix', 'quantite_stock', 'vendeur', 'date_publication')
    list_filter = ('zone_production', 'vendeur', 'date_publication')
    search_fields = ('nom', 'description', 'zone_production')
    readonly_fields = ('date_publication',) # date_publication remplace date_ajout

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Liste des colonnes à afficher
    list_display = ('user', 'role', 'telephone', 'ville')
    
    # Ajouter des filtres sur le côté
    list_filter = ('role', 'ville')
    
    # Ajouter une barre de recherche
    search_fields = ('user__username', 'telephone')
admin.site.register(LigneCommande)
# Personnalisation de l'interface d'administration
admin.site.site_header = "Administration AgriTech_GN"
admin.site.site_title = "Portail AgriTech Guinée"
admin.site.index_title = "Gestion de la plateforme"