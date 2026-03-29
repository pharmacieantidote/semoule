from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, DepotViewSet, VenteViewSet, current_user,PrixGlobalViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'depots', DepotViewSet)
router.register(r'ventes', VenteViewSet)
router.register(r'prix', PrixGlobalViewSet, basename='prix')

urlpatterns = [
    # ✅ IMPORTANT : Les routes personnalisées AVANT le router
    path('users/me/', current_user, name='current-user'),
    
    # Le router après (il ne catchera que les vrais IDs)
    path('', include(router.urls)),
]