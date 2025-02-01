# Wolt Delivery Order Price Calculator service

Wolt Delivery Order Price Calculator service API based on python fastapi to get delivery order price of the item including cart value and delivery fee according to the distance between user and venue.

# Wolt DOPC service Endpoints

- GET /healthz
    * Check healthz of service
- GET /api/v1/delivery-order-price
    * Calculate the total price including delivery fee and cart value according to the distance between user and venue 
  

# Backend development

## Installing dependencies

Install Python packages and dependencies

```shell
$ pip install virtualenv
$ python -m virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt 
```

# Build and Start for Development
You can build API server by command:

```shell
$ docker-compose up --build or python service/main.py
```

# Example usages
An example request to DOPC service look like this:

```shell
$ curl "http://localhost:8000/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000&user_lat=60.17094&user_lon=24.93087"
```
The endpoint return a JSON response in the following format:

```shell
{
  "total_price": 1190,
  "small_order_surcharge": 0,
  "cart_value": 1000,
  "delivery": {
    "fee": 190,
    "distance": 177
  }
}
```


## Run unit tests
Directly in command line in your desktop (note: may also use GUI editor such as VSCode)
```
$ python -m pytest       # or just 'pytest' (dependencies should be installed beforehand)
```

## Formatting (Python) code

The project uses black code formatter, run it with

```shell
$ black .
```
