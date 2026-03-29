# backend/create_superuser.py
import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # ← Vérifie que c'est bien le nom de ton projet
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 📦 Informations du superutilisateur
SUPERUSER_INFO = {
    'username': 'williams',
    'email': 'willyloseka@gmail.com',
    'password': 'nicalose',  # ⚠️ Change ce mot de passe en production !
    'role': User.Role.SUPERUSER if hasattr(User, 'Role') else 'SUPERUSER',  # ← Force le rôle SUPERUSER
}

def create_custom_superuser():
    """Crée un superutilisateur avec le rôle personnalisé SUPERUSER"""
    
    username = SUPERUSER_INFO['username']
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"⚠️ L'utilisateur '{username}' existe déjà.")
        
        # Mise à jour optionnelle : s'assurer qu'il est bien superuser + rôle correct
        updated = False
        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            updated = True
            print("   → Mise à jour : is_superuser = True")
        
        if hasattr(User, 'Role') and user.role != SUPERUSER_INFO['role']:
            user.role = SUPERUSER_INFO['role']
            updated = True
            print(f"   → Mise à jour : role = {SUPERUSER_INFO['role']}")
        
        if updated:
            user.save()
            print("✅ Utilisateur mis à jour avec les droits superadmin.")
        else:
            print("✅ Aucune modification nécessaire.")
        return
    
    # Création du superutilisateur
    print(f"🔐 Création du superutilisateur '{username}'...")
    
    try:
        # Méthode 1 : create_superuser (gère is_superuser=True automatiquement)
        user = User.objects.create_superuser(
            username=SUPERUSER_INFO['username'],
            email=SUPERUSER_INFO['email'],
            password=SUPERUSER_INFO['password'],
        )
        
        # Méthode 2 : Si ton modèle a un champ 'role' requis, le définir explicitement
        if hasattr(user, 'role') and SUPERUSER_INFO['role']:
            user.role = SUPERUSER_INFO['role']
            user.save(update_fields=['role'])
            print(f"   → Rôle défini : {SUPERUSER_INFO['role']}")
        
        print(f"✅ Superutilisateur '{username}' créé avec succès !")
        print(f"   • Email: {user.email}")
        print(f"   • Rôle: {user.role}")
        print(f"   • is_superuser: {user.is_superuser}")
        print(f"\n🔑 Tu peux maintenant te connecter avec :\n   Username: {username}\n   Password: {SUPERUSER_INFO['password']}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")
        print("\n💡 Si l'erreur mentionne 'role', assure-toi que le champ est nullable ou a une valeur par défaut dans models.py")

if __name__ == '__main__':
    create_custom_superuser()