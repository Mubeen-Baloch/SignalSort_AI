from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..models import User
from ..schemas import Register,Login
from ..auth import hash_password,verify_password,token_for,current_user
router=APIRouter(prefix='/auth',tags=['auth'])
def user_out(u):return {'id':str(u.id),'email':u.email,'name':u.name}
@router.post('/register')
async def register(body:Register,db:AsyncSession=Depends(get_db)):
    if (await db.execute(select(User).where(User.email==body.email))).scalar_one_or_none():raise HTTPException(409,'Email already registered')
    u=User(email=body.email,password_hash=hash_password(body.password),name=body.name);db.add(u);await db.commit();return {'token':token_for(u),'user':user_out(u)}
@router.post('/login')
async def login(body:Login,db:AsyncSession=Depends(get_db)):
    u=(await db.execute(select(User).where(User.email==body.email))).scalar_one_or_none()
    if not u or not verify_password(body.password,u.password_hash):raise HTTPException(401,'Invalid email or password')
    return {'token':token_for(u),'user':user_out(u)}
@router.get('/me')
async def me(u:User=Depends(current_user)):return user_out(u)
