import asyncio
from pathlib import Path
from sqlalchemy import select
from .db import Session
from .models import User,Community,Message,Intent
from .auth import hash_password
from .services.parser import parse_whatsapp
from .services.preprocessor import prepare
from .services.llm import fallback
from .services.embeddings import embed_texts
from .services.matcher import match_user
async def main():
 async with Session() as db:
  user=(await db.execute(select(User).where(User.email=='demo@signalsort.ai'))).scalar_one_or_none()
  if not user:
   user=User(email='demo@signalsort.ai',password_hash=hash_password('Demo@1234'),name='Demo User');db.add(user);await db.flush()
  community=(await db.execute(select(Community).where(Community.user_id==user.id,Community.source=='demo'))).scalar_one_or_none()
  if not community: community=Community(user_id=user.id,name='Global Leaders Community',source='demo');db.add(community);await db.flush()
  items=parse_whatsapp((Path(__file__).parent.parent/'seed'/'demo_chat.txt').read_text(encoding='utf-8'))
  # Fill the synthetic export out to a realistic 300-message community without
  # changing the useful signal posts at the top of the supplied transcript.
  senders=['Asha Kumar','Omar Reed','Lin Park','Diego Santos','Hana Lee','Arun Patel','Bea Wilson','Leo Tan']
  noise=['Good morning friends and have a wonderful day everyone.', 'Thank you for the helpful update shared with our community.', 'Lovely to see so many people supporting each other here.', 'Sharing positive energy with everyone in the group today.']
  from datetime import datetime
  for n in range(274):
   items.append({'sender':senders[n%len(senders)],'text':noise[n%len(noise)]+' Message number '+str(n+1),'timestamp':datetime(2024,3,13,9,n%60)})
  for x in items:
   p=prepare(x)
   if not p:continue
   if (await db.execute(select(Message.id).where(Message.community_id==community.id,Message.content_hash==p['content_hash']))).first():continue
   a=fallback(p['clean_text']);v=embed_texts([p['clean_text']+' '+a['summary']])[0]
   db.add(Message(community_id=community.id,sender=p['sender'],sent_at=p['timestamp'],raw_text=p['raw_text'],clean_text=p['clean_text'],urls=p['urls'],content_hash=p['content_hash'],category=a['category'],summary=a['summary'],entities=a['entities'],embedding=v,processed=True))
  defaults=[('Looking for healthcare tech projects to contribute to','I want to help build healthcare technology, health AI and accessible care projects.',.35),('Internships or jobs in data science and AI','Show paid internships and job opportunities in data science, machine learning and AI.',.38),('Hackathons, fellowships, and scholarships','Surface hackathons, fellowships, scholarships and program deadlines.',.35)]
  for title,desc,threshold in defaults:
   if not (await db.execute(select(Intent).where(Intent.user_id==user.id,Intent.title==title))).scalar_one_or_none():db.add(Intent(user_id=user.id,title=title,description=desc,threshold=threshold,embedding=embed_texts([title+' '+desc])[0]))
  await db.commit();await match_user(db,user.id);await db.commit()
if __name__=='__main__':asyncio.run(main())
