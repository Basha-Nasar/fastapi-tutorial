from fastapi import FastAPI
from app.routes.users import router as users_router
app = FastAPI()



app.include_router(users_router)

# items = [
#     {"id": 1, "name": "Item One"},
#     {"id": 2, "name": "Item Two"},
#     {"id": 3, "name": "Item Three"},

# ]

# @app.get('/health')
# def health_check():
#     return {'status' : "ok"}


# @app.get("/items")
# def getItems():
#     return items

# @app.get("/items/{item_id}")
# def get_item(item_id : int, page : int = 1):
#     for item in items:
#         if item['id'] == item_id:
#             return {"item" : item , "page" : page}
#     return {"error" : "Item Not Found"}


# @app.post("/items")
# def create_item(item: dict):
#     items.append(item)
#     return items