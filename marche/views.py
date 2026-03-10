from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Count, Sum, F
from django.http import HttpResponse
from django.template.loader import get_template
import io
from xhtml2pdf import pisa
from datetime import datetime  # Importation pour gérer l'heure

# Tes modèles et formulaires
from .models import Produit, Commande, LigneCommande, Categorie, Profile
from .forms import InscriptionAgriculteurForm, CommandeForm, ProduitForm, ProfileForm

# --- UTILS / CONTEXT PROCESSORS ---

def get_salutation():
    """Détermine la salutation en fonction de l'heure actuelle."""
    heure = datetime.now().hour
    if 5 <= heure < 12:
        return "Bonjour"
    elif 12 <= heure < 18:
        return "Bon après-midi"
    else:
        return "Bonsoir"

def is_agriculteur(user):
    return hasattr(user, 'profile') and user.profile.role == 'AGRI'

def panier_count(request):
    """Calcule le nombre total d'articles dans le panier (Context Processor)."""
    panier = request.session.get('panier', {})
    total_articles = sum(panier.values())
    return {'nb_articles_panier': total_articles}

# --- VUES CLIENTS ---

def index(request):
    query = request.GET.get('search')
    if query:
        # Filtrage par nom (insensible à la casse)
        produits = Produit.objects.filter(nom__icontains=query)
    else:
        produits = Produit.objects.all()
    
    # Ajout de la salutation dans le contexte
    context = {
        'produits': produits,
        'salutation': get_salutation()
    }
    
    return render(request, 'marche/index.html', context)

def ajouter_au_panier(request, produit_id):
    panier = request.session.get('panier', {})
    produit_id_str = str(produit_id)
    panier[produit_id_str] = panier.get(produit_id_str, 0) + 1
    request.session['panier'] = panier
    messages.success(request, "Produit ajouté au panier !")
    return redirect('index')

def voir_panier(request):
    panier = request.session.get('panier', {})
    articles_panier = []
    total = 0
    for p_id, qte in panier.items():
        try:
            p = Produit.objects.get(id=p_id)
            st = p.prix * qte
            total += st
            articles_panier.append({'produit': p, 'quantite': qte, 'sous_total': st})
        except Produit.DoesNotExist:
            continue
    return render(request, 'marche/panier.html', {'articles_panier': articles_panier, 'total': total})

def supprimer_du_panier(request, produit_id):
    panier = request.session.get('panier', {})
    if str(produit_id) in panier:
        del panier[str(produit_id)]
        request.session['panier'] = panier
    return redirect('voir_panier')

@login_required
def commander(request):
    panier = request.session.get('panier', {})
    if not panier: 
        return redirect('index')

    total = 0
    articles = []
    for p_id, qte in panier.items():
        p = get_object_or_404(Produit, id=p_id)
        total += p.prix * qte
        articles.append({'produit': p, 'quantite': qte})

    if request.method == 'POST':
        with transaction.atomic():
            # Correction ici : on s'assure que les noms correspondent au HTML et au Model
            commande = Commande.objects.create(
                client=request.user,
                total=total,
                adresse_livraison=request.POST.get('adresse_livraison') or request.POST.get('adresse'),
                telephone_contact=request.POST.get('telephone_contact') or request.POST.get('telephone')
            )
            
            for item in articles:
                produit = item['produit']
                quantite_commandee = item['quantite']

                if produit.quantite_stock >= quantite_commandee:
                    produit.quantite_stock -= quantite_commandee
                    produit.save()

                    LigneCommande.objects.create(
                        commande=commande,
                        produit=produit,
                        quantite=quantite_commandee,
                        prix_unitaire=produit.prix
                    )
                else:
                    messages.error(request, f"Désolé, le stock de {produit.nom} est insuffisant.")
                    return redirect('voir_panier')
            
            request.session['panier'] = {}
            messages.success(request, "Votre commande a été validée avec succès !")
            return render(request, 'marche/commande_succes.html', {'commande': commande})
            
    return render(request, 'marche/confirmer_commande.html', {'total': total})

# --- VUES AGRICULTEURS ---

def inscription_agriculteur(request):
    if request.method == 'POST':
        form = InscriptionAgriculteurForm(request.POST)
        if form.is_valid():
            user = form.save()
            groupe, _ = Group.objects.get_or_create(name='Agriculteurs')
            user.groups.add(groupe)
            messages.success(request, "Inscription réussie ! Connectez-vous.")
            return redirect('login')
    else:
        form = InscriptionAgriculteurForm()
    return render(request, 'registration/inscription.html', {'form': form})

@login_required
@user_passes_test(is_agriculteur, login_url='index')
def dashboard_agri(request):
    # On récupère les commandes qui contiennent au moins un produit du vendeur
    commandes = Commande.objects.filter(lignes__produit__vendeur=request.user).distinct().order_by('-date_commande')
    
    # ASTUCE : On calcule la part spécifique de ce vendeur pour chaque commande ici
    for cmd in commandes:
        cmd.ma_part = cmd.get_total_pour_vendeur(request.user)
    
    context = {
        'commandes': commandes,
        'revenu_total': sum(c.ma_part for c in commandes if c.statut == 'VALIDEE'),
        'mes_produits': Produit.objects.filter(vendeur=request.user),
    }
    return render(request, 'marche/dashboard_agri.html', context)

@user_passes_test(is_agriculteur, login_url='index')
@login_required
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        # On récupère les sélections des listes HTML
        nom_choisi = request.POST.get('nom')
        zone_choisie = request.POST.get('zone_production')

        if form.is_valid():
            produit = form.save(commit=False)
            produit.nom = nom_choisi
            produit.zone_production = zone_choisie
            produit.vendeur = request.user
            produit.save()
            return redirect('dashboard_agri')
    else:
        form = ProduitForm()
    return render(request, 'marche/ajouter_produit.html', {'form': form})

@login_required
def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id, vendeur=request.user)
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit mis à jour !")
            return redirect('dashboard_agri') 
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'marche/modifier_produit.html', {'form': form, 'produit': produit})

@login_required
def valider_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.statut = 'VALIDEE'
    commande.save()
    messages.success(request, "La commande a été marquée comme validée.")
    return redirect('dashboard_agri')

@login_required
def annuler_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.statut = 'ANNULEE'
    commande.save()
    messages.warning(request, "La commande a été annulée.")
    return redirect('dashboard_agri')

@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, id=pk, vendeur=request.user)
    if request.method == 'POST':
        produit.delete()
        messages.warning(request, "Produit retiré du marché.")
    return redirect('dashboard_agri')

# --- PROFIL ET DOCUMENTS ---

@login_required
def mon_profil(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour !")
            return redirect('mon_profil')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'marche/profil.html', {'form': form})

def generer_facture_pdf(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    
    template_path = 'marche/facture_pdf.html'
    context = {'commande': commande}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_AgriTech_{commande.id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Erreur lors de la génération du PDF", status=400)

from django.http import JsonResponse
from django.db.models import Count, Avg
from django.contrib.auth.models import User
from .models import Produit

def chatbot_logic(request):
    user_message = request.GET.get('message', '').lower()
    
    # 1. Détection des zones de Guinée
    zones_guinee = ['kindia', 'mamou', 'labé', 'kankan', 'boké', 'nzérékoré', 'faranah', 'conakry']
    zone_detectee = next((zone for zone in zones_guinee if zone in user_message), None)

    # 2. Gestion des PRIX (Recherche spécifique par produit)
    if 'prix' in user_message:
        produits = Produit.objects.all()
        produit_trouve = next((p for p in produits if p.nom.lower() in user_message), None)
        
        if produit_trouve:
            response = f"Le prix actuel pour : {produit_trouve.nom} est de {produit_trouve.prix} GNF."
        else:
            stats = Produit.objects.aggregate(Avg('prix'))
            prix_moyen = stats['prix__avg']
            if prix_moyen:
                response = f"Le prix moyen est de {round(prix_moyen, 2)} GNF. Précisez le nom d'un produit pour son prix exact."
            else:
                response = "Aucun prix n'est disponible pour le moment."

    # 3. Filtrage par ZONE GÉOGRAPHIQUE
    elif zone_detectee:
        produits_zone = Produit.objects.filter(zone_production__icontains=zone_detectee)
        if produits_zone.exists():
            noms = ", ".join([p.nom for p in produits_zone])
            response = f"À {zone_detectee.capitalize()}, nous avons : {noms}."
        else:
            response = f"Désolé, aucun produit enregistré provenant de {zone_detectee.capitalize()}."

    # 4. Liste des PRODUITS (Flexible avec "dispo")
    elif any(word in user_message for word in ['nom', 'disponible', 'dispo', 'vendez']):
        produits = Produit.objects.all().values_list('nom', flat=True)
        if produits:
            response = f"Les produits disponibles sur AgriTech GN sont : {', '.join(produits)}."
        else:
            response = "Le catalogue est vide actuellement."

    # 5. AGRICULTEUR le plus actif
    elif any(word in user_message for word in ['actif', 'vendeur', 'meilleur']):
        top_vendeur = User.objects.annotate(num_p=Count('produit')).order_by('-num_p').first()
        if top_vendeur and top_vendeur.num_p > 0:
            response = f"L'agriculteur le plus actif est {top_vendeur.username} avec {top_vendeur.num_p} produits."
        else:
            response = "Pas encore de statistiques de vente disponibles."

    # 6. Technique & Sécurité
    elif any(word in user_message for word in ['sécurité', 'données', 'mvc', 'django']):
        response = "AgriTech GN utilise Django (MVC) et une base de données relationnelle sécurisée pour protéger vos échanges."

    # 7. Réponse par défaut
    else:
        response = "Je suis l'expert AgriTech. Demandez-moi le prix d'un produit, les stocks par ville ou qui est le vendeur le plus actif !"

    return JsonResponse({'reply': response})