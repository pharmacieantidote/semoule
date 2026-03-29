from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Choix pour les rôles
class Role(models.TextChoices):
    SUPERUSER = 'SUPERUSER', 'Super Admin'
    DIRECTEUR = 'DIRECTEUR', 'Directeur Central'
    CHEF_DEPOT = 'CHEF_DEPOT', 'Chef de Dépôt'

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour gérer les rôles et l'appartenance à un dépôt.
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CHEF_DEPOT
    )
    # Un chef de depot est lié à un dépôt. Null pour Superuser/Directeur.
    depot = models.ForeignKey(
        'Depot', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='chefs'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Depot(models.Model):
    """
    Représente un dépôt physique de semoule.
    """
    nom = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    # Stock actuel de sacs de semoule dans ce dépôt
    stock_actuel = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.ville} (Stock: {self.stock_actuel})"

class Vente(models.Model):
    """
    Enregistre chaque vente de sacs de semoule.
    """
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name='ventes')
    vendeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantite = models.PositiveIntegerField()
    date_vente = models.DateTimeField(default=timezone.now)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Vente {self.quantite} sacs à {self.depot.nom} le {self.date_vente}"

    def save(self, *args, **kwargs):
        # Logique simple : décrémenter le stock lors de la vente
        # Note: Dans une app prod, on ferait cela via des transactions atomiques dans la Vue/API
        # Mais pour le modèle, on s'assure juste que la structure est là.
        super().save(*args, **kwargs)

# backend/core/models.py - À la fin du fichier

class PrixGlobal(models.Model):
    """
    Prix unique par sac de semoule, géré par le Superuser.
    Une seule instance existe dans toute la base.
    """
    prix_par_sac = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000.00,  # Prix par défaut : 1000 DA
        help_text="Prix de vente d'un sac de semoule en DA"
    )
    devise = models.CharField(max_length=10, default='usd', editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Prix Global"
        verbose_name_plural = "Prix Global"
    
    def __str__(self):
        return f"{self.prix_par_sac} {self.devise}/sac"
    
    def save(self, *args, **kwargs):
        # Force une seule instance dans la DB
        if not self.pk and PrixGlobal.objects.exists():
            raise Exception("Une seule instance de PrixGlobal est autorisée")
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_prix(cls):
        """Méthode utilitaire pour récupérer le prix facilement"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj.prix_par_sac