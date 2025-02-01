from pydantic import BaseModel

class DeliveryFee(BaseModel):
    fee: float
    distance: int

class DeliveryOrderPrice(BaseModel):
    total_price: float
    small_order_surcharge: float
    cart_value: float
    delivery: DeliveryFee