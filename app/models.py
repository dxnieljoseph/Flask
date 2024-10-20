from . import db

# Table intermédiaire pour la relation "likes" entre User et Post
likes = db.Table('likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)

# Modèle User
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user') 

    # Relation Many-to-Many avec Post via la table "likes"
    liked_posts = db.relationship('Post', secondary=likes, backref=db.backref('likers', lazy='dynamic'), overlaps="created_posts")

    # Relation One-to-Many vers les posts créés par l'utilisateur
    created_posts = db.relationship('Post', backref='author', lazy=True, overlaps="user_posts")

# Modèle Post
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relation vers le modèle User, avec un `overlaps` mis à jour pour éviter les conflits
    user = db.relationship('User', backref=db.backref('posts', lazy=True), overlaps="created_posts, author")
