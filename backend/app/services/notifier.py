from ..models import Notification
async def notify(db,user_id,match,message,intent):
    db.add(Notification(user_id=user_id,match_id=match.id,title=f'New match: {intent.title}',body=message.summary or message.clean_text[:160]))
