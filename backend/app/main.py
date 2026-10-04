import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, core
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
app=FastAPI(title='SignalSort AI')
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth.router);app.include_router(core.router)
@app.get('/health')
async def health():return {'status':'ok'}
