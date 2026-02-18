import unittest
from unittest.mock import patch, AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from http import HTTPStatus as hs

from service.main import app
from service.main import app
from service.db import get_db
from service.models.user import UserDb
from tests.util.auth_mock import mock_logged_in_user


class TestUserAuthentication(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Mock database session
        self.mock_db = AsyncMock(spec=AsyncSession)
        app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        self.client = None
        app.dependency_overrides = {}

    async def test_register_user(self):
        """Test user registration with a mocked database"""

        # ✅ Mock database behavior
        self.mock_db.execute.return_value.scalar_one_or_none = Mock(
            return_value=None
        )  # Simulate no existing user
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        response = self.client.post(
            "/api/v1/register",
            data={"username": "testuser", "password": "testpass"},
        )

        self.assertEqual(response.status_code, hs.OK)
        self.assertIn("User created successfully", response.json()["message"])

    async def test_register_existing_user(self):
        """Test registration of an existing user"""

        # ✅ Mock database behavior
        self.mock_db.execute.return_value.scalar_one_or_none = Mock(
            return_value=UserDb(username="testuser")
        )
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        response = self.client.post(
            "/api/v1/register",
            data={"username": "testuser", "password": "testpass"},
        )

        self.assertEqual(response.status_code, hs.BAD_REQUEST)
        self.assertIn("Username already registered", response.json()["detail"])

    @patch("service.auth.pwd_context.verify")
    async def test_login_user(self, mock_verify):
        """Test user login with correct credentials"""

        # ✅ Mock database behavior
        self.mock_db.execute.return_value.scalar_one_or_none = Mock(
            return_value=UserDb(username="testuser", password="testpass")
        )  # Simulate existing user
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        mock_verify.return_value = True

        response = self.client.post(
            "/api/v1/login",
            data={"username": "testuser", "password": "testpass"},
        )

        self.assertEqual(response.status_code, hs.OK)

    async def test_login_user_invalid_credentials(self):
        """Test user login with incorrect credentials"""

        # ✅ Mock database behavior
        self.mock_db.execute.return_value.scalar_one_or_none = Mock(
            return_value=None
        )  # Simulate no existing user
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()

        response = self.client.post(
            "/api/v1/login",
            data={"username": "testuser", "password": "wrongpass"},
        )

        self.assertEqual(response.status_code, hs.UNAUTHORIZED)
        self.assertIn("Invalid username or password", response.json()["detail"])

    async def test_logout(self):
        mock_logged_in_user(app)
        resp = self.client.post("/api/v1/logout")
        self.assertEqual(resp.status_code, hs.OK)
        self.assertNotIn("access-token", resp.cookies)
