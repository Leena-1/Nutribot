from fastapi import Header, HTTPException
from typing import Optional

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
        
    token = authorization.split(" ")[1]
    
    # Normally we would decode the JWT here and return the user payload.
    # Since the system used simulated tokens previously, we just return the token as ID.
    return {"token": token}
