"""
WSGI config for AgriTech_GN project.
Configuration optimisée pour la gestion des produits agricoles et factures PDF.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# 1. Sécurité pour l'encodage (évite les bugs de caractères spéciaux en production)
if sys.getdefaultencoding() != 'utf-8':
    import importlib
    importlib.reload(sys)

# 2. Définition du module de réglages
# On garde 'config.settings' car c'est le nom de ton dossier de configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 3. Initialisation de l'application WSGI
application = get_wsgi_application()