from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from http import HTTPStatus
from .models import Item, Cart, CartItem, ItemPost
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(title="Shop API")
Instrumentator().instrument(app).expose(app)

items: Dict[int, Item] = {}
carts: Dict[int, Cart] = {}


@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart():
    cart_id = len(carts) + 1
    carts[cart_id] = Cart(id=cart_id)
    return JSONResponse(content={"id": cart_id},
                        status_code=status.HTTP_201_CREATED,
                        headers={"Location": f"/cart/{cart_id}"})


@app.get("/cart/{id}")
def get_cart(id: int):
    if id not in carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    return carts[id]


@app.get("/cart")
def get_cart_list(offset: int = 0,
                  limit: int = 10,
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  min_quantity: Optional[int] = None,
                  max_quantity: Optional[int] = None):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail="Offset must be non-negative and Limit must be positive")
    for value in [min_price, max_price, min_quantity, max_quantity]:
        if value is not None and value < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Price and quantity must be a non-negative number")
    filtered_carts = [cart for cart in list(carts.values())[offset:offset + limit]
                      if (min_price is None or cart.price >= min_price) and
                      (max_price is None or cart.price <= max_price) and
                      (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
                      (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)]
    return filtered_carts


@app.post("/cart/{cart_id}/add/{item_id}")
def add_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts:
        raise HTTPException(status_code=404, detail="Cart not found")
    if item_id not in items or items[item_id].deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")
    item = items[item_id]
    cart = carts[cart_id]
    for cart_item in cart.items:
        if cart_item.id == item.id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1))
    cart.price += item.price
    return cart


@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemPost):
    item_id = len(items) + 1
    new_item = Item(id=item_id, name=item.name, price=item.price)
    items[item_id] = new_item
    return JSONResponse(
        content={"id": item_id, "name": new_item.name, "price": new_item.price},
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"/item/{item_id}"})


@app.get("/item/{id}", status_code=status.HTTP_200_OK)
def get_item(id: int):
    if id not in items or items[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item = items[id]
    return {"id": item.id, "name": item.name, "price": item.price}


@app.get("/item")
def get_item_list(offset: int = 0,
                  limit: int = 10,
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  show_deleted: bool = False):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail="Offset must be non-negative and limit positive")
    if any(val is not None and val < 0 for val in (min_price, max_price)):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Price must be non-negative")
    filtered_items = [item for item in list(items.values())[offset:offset + limit]
                      if (show_deleted or not item.deleted) and
                      (min_price is None or item.price >= min_price) and
                      (max_price is None or item.price <= max_price)]
    return filtered_items


@app.put("/item/{id}")
def update_item(id: int, item: ItemPost):
    if id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    new_item = Item(id=id, name=item.name, price=item.price)
    items[id] = new_item
    return {"id": new_item.id, "name": new_item.name, "price": new_item.price}


@app.patch("/item/{id}")
def patch_item(id: int, body: dict[str, Any]):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.deleted:
        raise HTTPException(status_code=304, detail="Item is deleted")
    allowed_fields = {"name", "price"}
    if any(field not in allowed_fields for field in body):
        raise HTTPException(status_code=422, detail="Invalid field in request body")
    for key, value in body.items():
        setattr(item, key, value)
    return {"id": item.id, "name": item.name, "price": item.price}


@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[id].deleted = True
    return {"message": "Item marked as deleted"}
