from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .db import get_db
from .models import User
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); bearer=HTTPBearer()
def hash_password(value): return pwd.hash(value)
def verify_password(value, hashed): return pwd.verify(value,hashed)
def token_for(user): return jwt.encode({'sub':str(user.id),'exp':datetime.now(timezone.utc)+timedelta(days=7)},settings.jwt_secret,algorithm='HS256')
async def current_user(credentials: HTTPAuthorizationCredentials=Depends(bearer), db: AsyncSession=Depends(get_db)):
    try: ident=jwt.decode(credentials.credentials,settings.jwt_secret,algorithms=['HS256'])['sub']
    except (JWTError,KeyError): raise HTTPException(401,'Invalid login token')
    user=await db.get(User,ident)
    if not user: raise HTTPException(401,'User not found')
    return user
