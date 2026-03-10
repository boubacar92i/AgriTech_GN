from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F

# 1. CATEGORIE
class Categorie(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    def __str__(self):
        return self.nom

# 2. PRODUIT
class Produit(models.Model):
    nom = models.CharField(max_length=100)
    zone_production = models.CharField(max_length=100, default="Kindia")
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    quantite_stock = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} ({self.zone_production})"

# 3. COMMANDE
class Commande(models.Model):
    STATUTS = [
        ('ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('ANNULEE', 'Annulée'), # Ajouté pour correspondre à ton HTML
        ('EN_COURS', 'En cours de livraison'),
        ('LIVREE', 'Livrée'),
    ]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commandes_passees")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    telephone_contact = models.CharField(max_length=20)
    adresse_livraison = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='ATTENTE')
    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.client.username}"

    # METHODE CRUCIALE POUR TON DASHBOARD
    def get_total_pour_vendeur(self, vendeur):
        """
        Calcule la part du revenu revenant à un vendeur spécifique
        pour cette commande.
        """
        from django.db.models import Sum, F
        return self.lignes.filter(produit__vendeur=vendeur).aggregate(
            total_part=Sum(F('quantite') * F('prix_unitaire'))
        )['total_part'] or 0

# 4. LIGNE DE COMMANDE
class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

# 5. PROFIL
class Profile(models.Model):
    ROLE_CHOICES = [('CLIENT', 'Client / Consommateur'), ('AGRI', 'Agriculteur / Producteur')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, default="Conakry")
    def __str__(self):
            return f"Profil de {self.user.username} ({self.get_role_display()})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()