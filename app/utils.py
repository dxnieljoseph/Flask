from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from .models import User  # Assurez-vous d'importer User depuis models.py

def role_required(required_role):
    """
    Un décorateur qui vérifie si l'utilisateur authentifié possède le rôle requis pour accéder à la ressource.
    
    :param required_role: Le rôle requis pour accéder à la route (par exemple, 'admin').
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()  # Obtenir les informations d'identité de l'utilisateur via le JWT
            user = User.query.filter_by(email=current_user['email']).first()  # Rechercher l'utilisateur en BD

            if not user:
                return jsonify({'message': 'Utilisateur non trouvé.'}), 404

            # Vérifier si l'utilisateur a le rôle requis
            if user.role != required_role:
                return jsonify({'message': f'Accès refusé, rôle {required_role} requis.'}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator
