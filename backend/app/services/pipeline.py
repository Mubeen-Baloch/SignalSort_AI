import logging
from sqlalchemy import select
from ..db import Session
from ..models import Job,Community,Message
from .preprocessor import prepare,chunks
from .llm import classify
from .embeddings import embed_texts
from .matcher import match_user
log=logging.getLogger(__name__)
async def run_job(job_id, items):
    async with Session() as db:
        job=await db.get(Job,job_id); job.status='processing'; job.total_messages=len(items);await db.commit()
        try:
            prepared=[c for x in items if (p:=prepare(x)) for c in chunks(p)]
            for start in range(0,len(prepared),10):
                batch=prepared[start:start+10]; analyses=await classify([x['clean_text'] for x in batch]); vectors=embed_texts([x['clean_text']+' '+a['summary']+' '+' '.join(sum(a['entities'].values(),[])) for x,a in zip(batch,analyses)])
                for x,a,v in zip(batch,analyses,vectors):
                    exists=(await db.execute(select(Message.id).where(Message.community_id==job.community_id,Message.content_hash==x['content_hash']))).first()
                    if not exists: db.add(Message(community_id=job.community_id,sender=x['sender'],sent_at=x.get('timestamp'),raw_text=x['raw_text'],clean_text=x['clean_text'],urls=x['urls'],content_hash=x['content_hash'],category=a['category'],summary=a['summary'],entities=a['entities'],embedding=v,processed=True))
                job.processed_messages=min(start+len(batch),len(prepared));await db.commit()
            community=await db.get(Community,job.community_id);await match_user(db,community.user_id);job.status='done';await db.commit()
        except Exception as e:
            log.exception('job failed');job.status='failed';job.error=str(e);await db.commit()
