import unittest
from unittest.mock import patch, MagicMock
from http import HTTPStatus as hs

from fastapi.testclient import TestClient
from service.main import app
from service.common.exceptions.AuthenticationException import AuthenticationException
from service.schema.user import User


class TestUserAuthentication(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def tearDown(self):
        self.client = None
        
        
    @patch.dict("service.auth.fake_db", side_effect=AuthenticationException("Wrong username or password"))
    async def test_login_with_invalid_credential(self):
        resp = self.client.post("/api/v1/login", data={"username": "invaliduser", "password": "invalidpassword"})

        self.assertEqual(resp.status_code, hs.UNAUTHORIZED)
        self.assertEqual(resp.json(), {"detail": "Wrong username or password"})

    async def test_login_with_none(self):
        resp = self.client.post("/api/v1/login", data={"username": None, "password": None})
        self.assertEqual(hs.BAD_REQUEST, resp.status_code)
    
    @patch("service.auth.fake_db", {"testuser": User(username="testuser", password="testpass")})
    async def test_successful_login(self):
    
        response = self.client.post("/api/v1/login", data={"username": "testuser", "password": "testpass"})
        
        self.assertEqual(hs.FOUND, response.status_code)
        self.assertIn("access-token", response.cookies)
    
    @patch('service.auth.load_user')
    @patch('service.auth.fake_db')
    def test_successful_login(self, mock_fake_db, mock_load_user):
        # Create mock user
        mock_user = MagicMock()
        mock_user.username = "user1"
        mock_user.password = "password1"

        # Configure the mock to return the mock user
        mock_fake_db.get.return_value = mock_user
        mock_load_user.return_value = mock_user
        
        # Create test user
        test_user = {
            "username": "user1",
            "password": "password1"
        }

        # Perform login
        response = self.client.post("/api/v1/login", data=test_user)
        
        # Assert response
        self.assertEqual(response.status_code, 302)
        self.assertIn("access-token", response.cookies)
    
    async def test_logout(self):
        resp = self.client.post("/api/v1/logout")
        self.assertEqual(resp.status_code, hs.FOUND)
        self.assertNotIn("access-token", resp.cookies)
