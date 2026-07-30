from fastapi import FastAPI
from models import product

app = FastAPI()

@app.get("/")
def greet():
    return "welcome to my world"

products = [
    product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    product(id=4, name="Table", description="A wooden table", price=199.99, quantity=20)
]

@app.get("/products")
def get_all_product():
    return products

@app.get("/product/{id}")
def get_product_by_id(id: int):
    for product in products:
        if product.id==id:
            return product

    return"product not found"

@app.post ("product")
def add_product(product:product):
    product.append(product)
    return product
