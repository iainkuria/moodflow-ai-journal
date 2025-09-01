import unittest
import json
from app import app, init_db

class MoodFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()

    def test_registration(self):
        response = self.app.post('/api/register', 
                               json={'username': 'test', 'email': 'test@test.com', 'password': 'password123'})
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        # First register
        self.app.post('/api/register', 
                     json={'username': 'test', 'email': 'test@test.com', 'password': 'password123'})
        # Then login
        response = self.app.post('/api/login', 
                               json={'username': 'test', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()