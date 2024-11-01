from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ..providers import jwt


security = HTTPBasic()

JWT_HASHED = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNhdWlha2lzbWUxIiwicGFzc3dvcmQiOiJzYXVpYWtsYXR1aTEyMyIsImlhdCI6MTIwOTIwMDN9.5zaHQ_nLPd6W8dpbxAX7tzZCWfmbXT14ZiNx-XRq334"


def password_middleware(cridentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    jwt_hash = jwt.encrypt({
        "username": cridentials.username,
        "password": cridentials.password
    })
    if jwt_hash != JWT_HASHED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )