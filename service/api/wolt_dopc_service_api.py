import os
from http import HTTPStatus as hs

from fastapi import APIRouter, HTTPException
from typing import Dict
from geopy.distance import geodesic

from service.common.rest_client import RestClient
from service.common.logger import logger
from service.model.dop import DeliveryOrderPrice

router = APIRouter()
client = RestClient()


@router.get("/api/v1/delivery-order-price", response_model=DeliveryOrderPrice)
async def calculate_delivery_price(
    venue_slug: str, cart_value: int, user_lat: float, user_lon: float
) -> Dict:
    logger.info(
        f"GET /api/v1/delivery-order-price params venue_slug {venue_slug}, cart_value {cart_value}, user_lat {user_lat}, user_lon {user_lon}"
    )

    HOME_ASSIGNMENT_API_URL = os.environ.get("HOME_ASSIGNMENT_API_URL", "default")
    MAX_DELIVERY_DISTANCE = 1000

    try:
        static_data = await client.get(f"{HOME_ASSIGNMENT_API_URL}/{venue_slug}/static")
        dynamic_data = await client.get(
            f"{HOME_ASSIGNMENT_API_URL}/{venue_slug}/dynamic"
        )
    except Exception as err:
        logger.error(f"Unexpected error occurred: {err}")
        raise HTTPException(status_code=hs.INTERNAL_SERVER_ERROR, detail=err)

    # Calculate delivery distance
    venue_coords = static_data["venue_raw"]["location"]["coordinates"]
    if not venue_coords or len(venue_coords) != 2:
        raise HTTPException(
            status_code=hs.INTERNAL_SERVER_ERROR, detail="Invalid venue location data"
        )

    venue_lon, venue_lat = venue_coords
    user_location = (user_lat, user_lon)
    venue_location = (venue_lat, venue_lon)
    distance = int(geodesic(user_location, venue_location).meters)

    logger.info(f"Calculated distance: {distance} meters")

    if distance >= MAX_DELIVERY_DISTANCE:
        logger.warning(f"Delivery not possible for distance: {distance} meters")
        raise HTTPException(
            status_code=hs.BAD_REQUEST,
            detail=f"Delivery not possible for distances of {MAX_DELIVERY_DISTANCE} meters or more. Current distance: {distance} meters",
        )

    # Extract required dynamic data
    order_minimum_no_surcharge = dynamic_data["venue_raw"]["delivery_specs"]["order_minimum_no_surcharge"]
    base_price = dynamic_data["venue_raw"]["delivery_specs"]["delivery_pricing"]["base_price"]
    distance_ranges = dynamic_data["venue_raw"]["delivery_specs"]["delivery_pricing"]["distance_ranges"]

    delivery_fee = None
    for range_info in distance_ranges:
        min_dist = range_info["min"]
        max_dist = range_info["max"]
        a = range_info["a"]
        b = range_info["b"]

        if max_dist == 0 or (min_dist <= distance < max_dist):
            delivery_fee = base_price + a + round(b * distance / 10)
            break

    small_order_surcharge = max(0, order_minimum_no_surcharge - cart_value)
    total_price = cart_value + small_order_surcharge + delivery_fee

    return {
        "total_price": total_price,
        "small_order_surcharge": small_order_surcharge,
        "cart_value": cart_value,
        "delivery": {"fee": delivery_fee, "distance": distance},
    }
