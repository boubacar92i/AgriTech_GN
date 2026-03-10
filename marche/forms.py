from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Commande, Produit, Profile

class InscriptionAgriculteurForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['telephone_contact', 'adresse_livraison']

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['prix', 'quantite_stock', 'description', 'image']
        widgets = {
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix en GNF'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'telephone', 'adresse', 'ville']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
        }