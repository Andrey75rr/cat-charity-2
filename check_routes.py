from app.main import app

print("Зарегистрированные маршруты:")
for route in app.routes:
    print(f"{list(route.methods)} {route.path}")