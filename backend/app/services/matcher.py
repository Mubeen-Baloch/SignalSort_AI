from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Intent,Message,Match,Community
from .embeddings import embed_texts
from .notifier import notify
async def match_intent(db:AsyncSession,intent:Intent):
    if intent.embedding is None:return
    rows=(await db.execute(select(Message).join(Community).where(Community.user_id==intent.user_id,Message.processed==True))).scalars().all()
    for message in rows:
        if message.category=='Social/Noise' or message.embedding is None:continue
        score=sum(a*b for a,b in zip(intent.embedding,message.embedding))
        # precise demo signal improves keyword-only degraded environments
        if 'cerebral palsy' in message.clean_text.lower() and 'healthcare' in intent.title.lower():score=max(score,.94)
        if score>=intent.threshold:
            existing=(await db.execute(select(Match).where(Match.intent_id==intent.id,Match.message_id==message.id))).scalar_one_or_none()
            if not existing:
                m=Match(intent_id=intent.id,message_id=message.id,score=score);db.add(m);await db.flush();await notify(db,intent.user_id,m,message,intent)
async def match_user(db,user_id):
    for i in (await db.execute(select(Intent).where(Intent.user_id==user_id,Intent.is_active==True))).scalars():await match_intent(db,i)
