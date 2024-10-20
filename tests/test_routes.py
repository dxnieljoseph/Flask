import unittest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

class APITestCase(unittest.TestCase):
    
    def setUp(self):
        """Configurer l'application Flask et la base de données de test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire pour les tests
        self.client = self.app.test_client()

        # Crée un contexte de base de données et initialise la base
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Nettoyer après les tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_user(self):
        """Tester l'enregistrement d'un utilisateur."""
        response = self.client.post('/register', json={
            'username': 'testuser',
            'email': 'testuser@mail.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 201)
        # Vérifier la réponse Unicode
        self.assertIn('Utilisateur créé avec succès', response.get_json()['message'])
    
    def test_login(self):
        """Tester la connexion d'un utilisateur."""
        # Créer un utilisateur avec un mot de passe haché
        with self.app.app_context():
            hashed_password = generate_password_hash('testpassword', method='pbkdf2:sha256')
            user = User(username='testuser', email='testuser@mail.com', password=hashed_password)
            db.session.add(user)
            db.session.commit()

        # Essayer de se connecter avec le mot de passe en clair
        response = self.client.post('/login', json={
            'email': 'testuser@mail.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

if __name__ == '__main__':
    unittest.main()
