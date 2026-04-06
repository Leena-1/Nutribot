import asyncio
from backend.routes.auth_routes import SignupRequest, signup
from pydantic import ValidationError

async def test():
    try:
        req = SignupRequest(
            email="test_auto@example.com",
            password="testpassword",
            age=25,
            weight=70.5,
            diseases=["None"]
        )
        print("Starting signup...")
        res = await signup(req)
        print(f"Result: {res}")
    except Exception as e:
        import traceback
        print("CRASH FOUND:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
