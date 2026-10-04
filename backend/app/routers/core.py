from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,BackgroundTasks
from pathlib import Path
from sqlalchemy import select,func,delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..db import get_db
from ..models import *
from ..auth import current_user
from ..schemas import *
from ..services.parser import parse_whatsapp
from ..services.pipeline import run_job
from ..services.embeddings import embed_texts
from ..services.matcher import match_intent
router=APIRouter(tags=['app'])
def own(stmt, user):return stmt
async def community_for(db,id,user):
    c=await db.get(Community,id)
    if not c or c.user_id!=user.id:raise HTTPException(404,'Community not found')
    return c
@router.get('/me')
async def me_alias(u:User=Depends(current_user)):return {'id':str(u.id),'email':u.email,'name':u.name}
@router.post('/communities')
async def create_community(body:CommunityIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    c=Community(user_id=u.id,name=body.name,source=body.source);db.add(c);await db.commit();return {'id':str(c.id),'name':c.name,'source':c.source}
@router.get('/communities')
async def communities(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return [{'id':str(x.id),'name':x.name,'source':x.source} for x in (await db.execute(select(Community).where(Community.user_id==u.id))).scalars()]
async def begin(db,bg,c,items):
    j=Job(community_id=c.id,total_messages=len(items));db.add(j);await db.commit();bg.add_task(run_job,j.id,items);return {'job_id':str(j.id)}
@router.post('/ingest/paste')
async def paste(body:PasteIn,bg:BackgroundTasks,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return await begin(db,bg,await community_for(db,body.community_id,u),parse_whatsapp(body.text))
@router.post('/ingest/demo')
async def demo_import(bg:BackgroundTasks,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    c=(await db.execute(select(Community).where(Community.user_id==u.id,Community.name=='Global Leaders Community'))).scalar_one_or_none()
    if not c:
        c=Community(user_id=u.id,name='Global Leaders Community',source='demo');db.add(c);await db.flush()
    text=(Path(__file__).resolve().parents[2]/'seed'/'demo_chat.txt').read_text(encoding='utf-8')
    return await begin(db,bg,c,parse_whatsapp(text))
@router.post('/ingest/upload')
async def upload(community_id:UUID,bg:BackgroundTasks,file:UploadFile=File(...),u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return await begin(db,bg,await community_for(db,community_id,u),parse_whatsapp((await file.read()).decode('utf-8','ignore')))
@router.post('/ingest/webhook')
async def webhook(body:WebhookIn,bg:BackgroundTasks,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return await begin(db,bg,await community_for(db,body.community_id,u),[x.model_dump() for x in body.messages])
@router.get('/jobs/{job_id}')
async def job(job_id:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    j=await db.get(Job,job_id);await community_for(db,j.community_id,u) if j else (_ for _ in ()).throw(HTTPException(404,'Job not found'));return {'id':str(j.id),'status':j.status,'total_messages':j.total_messages,'processed_messages':j.processed_messages,'error':j.error}
@router.get('/messages')
async def messages(category:str|None=None,community:UUID|None=None,search:str|None=None,page:int=1,limit:int=50,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    q=select(Message,Community.name).join(Community).where(Community.user_id==u.id)
    if category:q=q.where(Message.category==category)
    if community:q=q.where(Message.community_id==community)
    if search:q=q.where(Message.clean_text.ilike(f'%{search}%'))
    rows=(await db.execute(q.order_by(Message.sent_at.desc()).offset((page-1)*limit).limit(limit))).all()
    return [{'id':str(m.id),'sender':m.sender,'text':m.raw_text,'summary':m.summary,'category':m.category,'entities':m.entities,'community':n,'sent_at':m.sent_at} for m,n in rows]
@router.get('/digest')
async def digest(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Message).join(Community).where(Community.user_id==u.id,Message.processed==True))).scalars();out={}
    for m in rows:out.setdefault(m.category,[]).append({'id':str(m.id),'summary':m.summary,'entities':m.entities})
    return out
@router.get('/intents')
async def intents(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return [{'id':str(i.id),'title':i.title,'description':i.description,'threshold':i.threshold,'is_active':i.is_active} for i in (await db.execute(select(Intent).where(Intent.user_id==u.id))).scalars()]
@router.post('/intents')
async def create_intent(body:IntentIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    i=Intent(user_id=u.id,**body.model_dump(),embedding=embed_texts([body.title+' '+body.description])[0]);db.add(i);await db.flush();await match_intent(db,i);await db.commit();return {'id':str(i.id)}
@router.put('/intents/{intent_id}')
async def update_intent(intent_id:UUID,body:IntentIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    i=await db.get(Intent,intent_id)
    if not i or i.user_id!=u.id:raise HTTPException(404,'Intent not found')
    for k,v in body.model_dump().items():setattr(i,k,v)
    i.embedding=embed_texts([i.title+' '+i.description])[0];await db.execute(delete(Match).where(Match.intent_id==i.id));await db.flush();await match_intent(db,i);await db.commit();return {'ok':True}
@router.delete('/intents/{intent_id}')
async def delete_intent(intent_id:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    i=await db.get(Intent,intent_id)
    if not i or i.user_id!=u.id:raise HTTPException(404,'Intent not found')
    await db.delete(i);await db.commit();return {'ok':True}
@router.get('/matches')
async def matches(intent:UUID|None=None,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    q=select(Match,Message,Intent).join(Message,Match.message_id==Message.id).join(Intent,Match.intent_id==Intent.id).where(Intent.user_id==u.id)
    if intent:q=q.where(Intent.id==intent)
    return [{'id':str(a.id),'score':round(a.score*100),'seen':a.seen,'intent':c.title,'sender':b.sender,'text':b.raw_text,'summary':b.summary,'entities':b.entities,'sent_at':b.sent_at} for a,b,c in (await db.execute(q.order_by(Match.score.desc()))).all()]
@router.post('/matches/{match_id}/seen')
async def seen(match_id:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    m=await db.get(Match,match_id);i=await db.get(Intent,m.intent_id) if m else None
    if not i or i.user_id!=u.id:raise HTTPException(404,'Match not found')
    m.seen=True;await db.commit();return {'ok':True}
@router.get('/notifications')
async def notifications(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    return [{'id':str(n.id),'title':n.title,'body':n.body,'read':n.read,'created_at':n.created_at} for n in (await db.execute(select(Notification).where(Notification.user_id==u.id).order_by(Notification.created_at.desc()))).scalars()]
@router.post('/notifications/{notification_id}/read')
async def read(notification_id:UUID,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    n=await db.get(Notification,notification_id)
    if not n or n.user_id!=u.id:raise HTTPException(404,'Notification not found')
    n.read=True;await db.commit();return {'ok':True}
