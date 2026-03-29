# backend/core/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Sum, Q
from rest_framework import serializers  # ← Important pour les validations

from .models import User, Depot, Vente
from .serializers import UserSerializer, DepotSerializer, VenteSerializer
from .permissions import IsSuperUser, IsDirectorOrSuperUser


# --- User ViewSet ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.none()


# --- Depot ViewSet ---
class DepotViewSet(viewsets.ModelViewSet):
    queryset = Depot.objects.all()
    serializer_class = DepotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # ✅ CORRECTION : Utiliser les strings directement au lieu de User.Role.XXX
        if user.is_superuser or user.role == 'DIRECTEUR':
            return Depot.objects.all()
        elif user.role == 'CHEF_DEPOT':
            # ✅ Sécurité : vérifier que user.depot existe avant de filtrer
            if user.depot:
                return Depot.objects.filter(id=user.depot.id)
            return Depot.objects.none()
        return Depot.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsSuperUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='stats')
    def global_stats(self, request):
        total_depots = Depot.objects.count()
        total_stock = Depot.objects.aggregate(total=Sum('stock_actuel'))['total'] or 0
        
        today = timezone.now().date()
        ventes_today = Vente.objects.filter(date_vente__date=today)
        total_ventes_today = ventes_today.aggregate(total=Sum('quantite'))['total'] or 0
        revenue_today = total_ventes_today * 1  # Prix unitaire à adapter
        
        top_depots = Depot.objects.order_by('-stock_actuel')[:5].values('nom', 'ville', 'stock_actuel')
        
        return Response({
            'total_depots': total_depots,
            'total_stock': total_stock,
            'ventes_today': total_ventes_today,
            'revenue_today': revenue_today,
            'top_depots': list(top_depots)
        })


# --- Vente ViewSet ---
class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'DIRECTEUR':
            return Vente.objects.all().order_by('-date_vente')
        elif user.role == 'CHEF_DEPOT':
            if user.depot:
                return Vente.objects.filter(depot=user.depot).order_by('-date_vente')
            return Vente.objects.none()
        return Vente.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        depot = serializer.validated_data['depot']
        quantite = serializer.validated_data['quantite']

        # Sécurité : un chef ne peut vendre que dans SON dépôt
        if user.role == 'CHEF_DEPOT' and user.depot != depot:
            raise permissions.PermissionDenied("Vous ne pouvez vendre que dans votre dépôt.")

        # Vérification du stock
        if depot.stock_actuel < quantite:
            raise serializers.ValidationError("Stock insuffisant pour cette vente.")

        # Décrémentation du stock
        depot.stock_actuel -= quantite
        depot.save()
        
        serializer.save(vendeur=user)


# --- Endpoint current_user ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PrixGlobal

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Retourne les infos de l'utilisateur connecté"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# backend/core/views.py - Ajoute à la fin

from .models import PrixGlobal
from .serializers import PrixGlobalSerializer

# backend/core/views.py

class PrixGlobalViewSet(viewsets.ModelViewSet):
    """
    Gestion du prix global :
    - Lecture (GET) : Tous les utilisateurs authentifiés
    - Écriture (POST/PUT/PATCH/DELETE) : Superuser uniquement
    """
    queryset = PrixGlobal.objects.all()
    serializer_class = PrixGlobalSerializer
    
    # ✅ Permission dynamique selon l'action
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # ✅ Seul le Superuser peut modifier le prix
            return [permissions.IsAuthenticated(), IsSuperUser()]
        # ✅ Tous les utilisateurs authentifiés peuvent lire le prix
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        # Retourne toujours l'instance unique (pk=1)
        obj, created = PrixGlobal.objects.get_or_create(pk=1)
        return PrixGlobal.objects.filter(pk=1)
    
    @action(detail=False, methods=['get'], url_path='current')
    def get_current_price(self, request):
        """Endpoint public (auth requis) pour récupérer le prix actuel"""
        prix = PrixGlobal.get_prix()
        obj = PrixGlobal.objects.get(pk=1)
        return Response({
            'prix_par_sac': float(prix), 
            'devise': obj.devise
        })