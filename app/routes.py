from flask import jsonify, request, Blueprint
from .models import User, Post
from .schemas import UserSchema, PostSchema
from . import db
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .utils import role_required  # Importer le décorateur depuis utils.py

# Créer un blueprint pour les routes
routes = Blueprint('routes', __name__)

# Schéma pour les utilisateurs et posts
user_schema = UserSchema()  # Pour un utilisateur
users_schema = UserSchema(many=True)  # Pour plusieurs utilisateurs
post_schema = PostSchema()  # Pour un post
posts_schema = PostSchema(many=True)  # Pour plusieurs posts

# Route pour l'URL racine
@routes.route('/', methods=['GET'])
def index():
    return "Bienvenue sur l'API !", 200

# Route pour obtenir tous les utilisateurs
@routes.route('/users', methods=['GET'])
@jwt_required()  # Protéger l'accès avec JWT
def get_users():
    users = User.query.all()
    if not users:
        return jsonify({"message": "Aucun utilisateur trouvé"}), 404
    return jsonify(users_schema.dump(users)), 200

# Route pour obtenir un utilisateur par ID
@routes.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'role': user.role
        }), 200
    return jsonify({'message': 'Utilisateur non trouvé'}), 404


# Route pour ajouter un utilisateur
@routes.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    try:
        new_user = user_schema.load(request.json, session=db.session)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

# Route pour mettre à jour un utilisateur
@routes.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    db.session.commit()

    return user_schema.jsonify(user), 200

# Route pour supprimer un utilisateur
@routes.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404

    db.session.delete(user)
    db.session.commit()
    return '', 204

# Route pour l'enregistrement
@routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Cet utilisateur existe déjà.'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur créé avec succès.'}), 201

# Route pour la connexion
@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Identifiants incorrects'}), 401

    access_token = create_access_token(identity={'username': user.username, 'email': user.email})
    return jsonify(access_token=access_token), 200

# Route protégée pour les utilisateurs connectés
@routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Route réservée aux administrateurs
@routes.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()

    if user.role != 'admin':
        return jsonify({'message': 'Accès refusé, administrateurs uniquement.'}), 403

    return jsonify({'message': 'Bienvenue dans la section administrateur.'}), 200

# Route utilisant le décorateur personnalisé role_required
@routes.route('/admin_only', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_route():
    return jsonify({'message': 'Bienvenue, administrateur.'}), 200

# Route du tableau de bord pour les utilisateurs connectés
@routes.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Bienvenue {current_user["username"]}, vous êtes connecté.'}), 200

# Route pour obtenir tous les posts
@routes.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    posts = Post.query.all()
    return jsonify(posts_schema.dump(posts)), 200

# Route pour créer un post
@routes.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    try:
        new_post = post_schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(new_post)
    db.session.commit()
    return post_schema.jsonify(new_post), 201

# Route pour obtenir un post par ID
@routes.route('/posts/<int:id>', methods=['GET'])
@jwt_required()
def get_post_by_id(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'message': 'Post non trouvé'}), 404
    return post_schema.jsonify(post), 200

# Route pour mettre à jour un post
@routes.route('/posts/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'message': 'Post non trouvé'}), 404

    data = request.get_json()
    post.title = data.get('title', post.title)
    post.body = data.get('body', post.body)
    db.session.commit()

    return post_schema.jsonify(post), 200

# Route pour supprimer un post
@routes.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'message': 'Post non trouvé'}), 404

    db.session.delete(post)
    db.session.commit()
    return '', 204
