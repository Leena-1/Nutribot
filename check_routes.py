from backend.main import app
print("--- ALL ROUTES ---")
for route in app.routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f"{methods} {route.path}")
print("--- END ---")
