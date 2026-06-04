from fastapi import Depends, HTTPException
from app.core.jwt_handle import oauth_scheme, verify_token

async def get_current_username(token: str = Depends(oauth_scheme)):

    try:
        username = verify_token(token)
        return username
    except:
        raise HTTPException(status_code=401, detail="Invalid token")