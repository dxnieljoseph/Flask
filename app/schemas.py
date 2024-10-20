from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import User, Post

# Schéma pour le modèle User
class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  # Désérialisation pour créer des instances User
        include_relationships = True  # Inclure les relations dans la sérialisation
        exclude = ('password',)  # Exclure le champ password de la sérialisation

    # On peut spécifier les champs que l'on souhaite exposer dans l'API
    id = fields.Int(dump_only=True)  # Le champ ID est seulement en lecture
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(required=True)  # Inclure le rôle de l'utilisateur dans la sérialisation
    liked_posts = fields.List(fields.Nested('PostSchema', only=['id', 'title']))  # Nester le schéma des Posts

# Schéma pour le modèle Post
class PostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True  # Inclure les clés étrangères dans la sérialisation

    # Champs à exposer
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    body = fields.Str(required=True)
    user = fields.Nested(UserSchema, only=['id', 'username'])  # Inclure l'auteur (User)
