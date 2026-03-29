# backend/core/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Depot, Vente

User = get_user_model()


class DepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = ['id', 'nom', 'ville', 'stock_actuel', 'date_creation']
        read_only_fields = ['date_creation']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    # ✅ Pour l'AFFICHAGE : retourne les détails du dépôt (lecture seule)
    depot = DepotSerializer(read_only=True)
    
    # ✅ Pour la CRÉATION : accepte un ID de dépôt (écriture seule)
    depot_id = serializers.PrimaryKeyRelatedField(
        queryset=Depot.objects.all(),
        source='depot',  # Lie depot_id au champ 'depot' du modèle
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 
            'role', 'depot', 'depot_id',  # ← Ajouter depot_id ici
            'is_staff', 'is_superuser'
        ]
        read_only_fields = ['is_staff', 'is_superuser']

    def create(self, validated_data):
        # ✅ Force is_active=True pour tout nouvel utilisateur
        validated_data['is_active'] = True
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # ✅ Empêche de modifier is_active via l'API
        validated_data.pop('is_active', None)
        return super().update(instance, validated_data)


class VenteSerializer(serializers.ModelSerializer):
    depot_nom = serializers.CharField(source='depot.nom', read_only=True)
    vendeur_nom = serializers.CharField(source='vendeur.username', read_only=True)
    # ✅ Champ calculé : revenue = quantité × prix global
    revenue = serializers.SerializerMethodField(read_only=True)
    prix_unitaire = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Vente
        fields = [
            'id', 'depot', 'depot_nom', 
            'vendeur', 'vendeur_nom', 
            'quantite', 'date_vente', 'commentaire',
            'revenue', 'prix_unitaire'  # ← Ajouter ces champs
        ]
        read_only_fields = ['vendeur', 'date_vente', 'revenue', 'prix_unitaire']

    def get_prix_unitaire(self, obj):
        return float(PrixGlobal.get_prix())
    
    def get_revenue(self, obj):
        prix = PrixGlobal.get_prix()
        return float(prix * obj.quantite)

    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0.")
        return value

from .models import PrixGlobal

class PrixGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrixGlobal
        fields = ['id', 'prix_par_sac', 'devise', 'updated_at']
        read_only_fields = ['devise', 'updated_at']