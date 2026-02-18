from http import HTTPStatus as hs
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from service.main import app
from tests.util.auth_mock import mock_logged_in_user
from service.common.rest_client import RestClient


mock_static_data = {"venue_raw": {"location": {"coordinates": [24.9415, 60.1699]}}}

mock_dynamic_data = {
    "venue_raw": {
        "delivery_specs": {
            "order_minimum_no_surcharge": 600,
            "delivery_pricing": {
                "base_price": 100,
                "distance_ranges": [
                    {"min": 0, "max": 500, "a": 1, "b": 0},
                    {"min": 500, "max": 1000, "a": 50, "b": 2},
                    {"min": 1000, "max": 2000, "a": 50, "b": 2},
                ],
            },
        }
    }
}


class TestDeliveryOrderPriceService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
        mock_logged_in_user(app)

    def tearDown(self):
        self.client = None

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(hs.OK, resp.status_code)
        self.assertEqual(resp.json(), {"status": "ok"})

    @patch.object(RestClient, "get")
    async def test_get_delivery_order_price_success(self, mock_get):

        mock_get.side_effect = [mock_static_data, mock_dynamic_data]

        resp = self.client.get(
            "/api/v1/delivery-order-price",
            params={
                "venue_slug": "mock-venue",
                "cart_value": 9999,
                "user_lat": 60.1709,
                "user_lon": 24.93087,
            },
        )

        expected_resp = {
            "total_price": 10269,
            "small_order_surcharge": 0,
            "cart_value": 9999,
            "delivery": {"distance": 600, "fee": 270},
        }

        self.assertEqual(hs.OK, resp.status_code)
        self.assertEqual(expected_resp, resp.json())

    @patch.object(RestClient, "get")
    async def test_get_delivery_exceeds_max_distance(self, mock_get):

        mock_get.side_effect = [mock_static_data, mock_dynamic_data]

        resp = self.client.get(
            "/api/v1/delivery-order-price",
            params={
                "venue_slug": "mock-venue",
                "cart_value": 9999,
                "user_lat": 60.1709,
                "user_lon": 40.93087,
            },
        )

        expected_resp = {
            "detail": "Delivery not possible for distances of 1000 meters or more. Current distance: 885444 meters"
        }

        self.assertEqual(hs.BAD_REQUEST, resp.status_code)
        self.assertEqual(expected_resp, resp.json())

    @patch.object(RestClient, "get")
    async def test_get_delivery_with_added_surcharge_amount(self, mock_get):

        mock_get.side_effect = [mock_static_data, mock_dynamic_data]

        resp = self.client.get(
            "/api/v1/delivery-order-price",
            params={
                "venue_slug": "mock-venue",
                "cart_value": 100,
                "user_lat": 60.1709,
                "user_lon": 24.93087,
            },
        )
        self.assertEqual(hs.OK, resp.status_code)
        self.assertGreater(resp.json()["small_order_surcharge"], 0)
