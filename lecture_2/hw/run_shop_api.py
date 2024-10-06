import requests
import random
import time

BASE_URL = "http://localhost:8000"

def create_item(name: str, price: float):
    url = f"{BASE_URL}/item"
    data = {"name": name, "price": price}
    response = requests.post(url, json=data)
    return response.json()

def create_cart():
    url = f"{BASE_URL}/cart"
    response = requests.post(url)
    return response.json()

def add_item_to_cart(cart_id: int, item_id: int):
    url = f"{BASE_URL}/cart/{cart_id}/add/{item_id}"
    response = requests.post(url)
    return response.json()

def get_cart(cart_id: int):
    url = f"{BASE_URL}/cart/{cart_id}"
    response = requests.get(url)
    return response.json()

def get_item(item_id: int):
    url = f"{BASE_URL}/item/{item_id}"
    response = requests.get(url)
    return response.json()

def main():
    for i in range(100):
        item_name = f"Item{i+1}"
        item_price = round(random.uniform(5.0, 50.0), 2)
        item = create_item(item_name, item_price)

        cart = create_cart()

        for _ in range(random.randint(1, 5)):
            add_item_to_cart(cart['id'], item['id'])

        cart_details = get_cart(cart['id'])

        if random.random() < 0.2:
            fake_item_id = random.randint(1000, 9999)
            error_response = add_item_to_cart(cart['id'], fake_item_id)
            print(f"Error response for adding item ID {fake_item_id}: {error_response}")

        time.sleep(0.5)

if __name__ == "__main__":
    main()
