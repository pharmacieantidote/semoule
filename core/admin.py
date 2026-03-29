from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Depot, Vente

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'depot', 'email', 'is_staff')
    list_filter = ('role', 'depot')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Métier', {'fields': ('role', 'depot')}),
    )

@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'stock_actuel')
    search_fields = ('nom', 'ville')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('date_vente', 'depot', 'vendeur', 'quantite')
    list_filter = ('date_vente', 'depot')
