import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Float, Integer, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase): pass
def uid(): return uuid.uuid4()
class User(Base):
    __tablename__='users'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); email: Mapped[str]=mapped_column(String,unique=True); password_hash: Mapped[str]=mapped_column(String); name: Mapped[str]=mapped_column(String); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class Community(Base):
    __tablename__='communities'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id')); name: Mapped[str]=mapped_column(String); source: Mapped[str]=mapped_column(String); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class Message(Base):
    __tablename__='messages'; __table_args__=(UniqueConstraint('community_id','content_hash'),); id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); community_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('communities.id')); sender: Mapped[str]=mapped_column(String); sent_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True); raw_text: Mapped[str]=mapped_column(Text); clean_text: Mapped[str]=mapped_column(Text); urls: Mapped[list]=mapped_column(JSON,default=list); content_hash: Mapped[str]=mapped_column(String); category: Mapped[str|None]=mapped_column(String,nullable=True); summary: Mapped[str|None]=mapped_column(Text,nullable=True); entities: Mapped[dict]=mapped_column(JSON,default=dict); embedding: Mapped[list|None]=mapped_column(Vector(384),nullable=True); processed: Mapped[bool]=mapped_column(Boolean,default=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class Intent(Base):
    __tablename__='listening_intents'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id')); title: Mapped[str]=mapped_column(String); description: Mapped[str]=mapped_column(Text); embedding: Mapped[list|None]=mapped_column(Vector(384),nullable=True); threshold: Mapped[float]=mapped_column(Float,default=.5); is_active: Mapped[bool]=mapped_column(Boolean,default=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class Match(Base):
    __tablename__='matches'; __table_args__=(UniqueConstraint('intent_id','message_id'),); id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); intent_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('listening_intents.id')); message_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('messages.id')); score: Mapped[float]=mapped_column(Float); notified: Mapped[bool]=mapped_column(Boolean,default=False); seen: Mapped[bool]=mapped_column(Boolean,default=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class Job(Base):
    __tablename__='jobs'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); community_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('communities.id')); status: Mapped[str]=mapped_column(String,default='pending'); total_messages: Mapped[int]=mapped_column(Integer,default=0); processed_messages: Mapped[int]=mapped_column(Integer,default=0); error: Mapped[str|None]=mapped_column(Text,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow,onupdate=datetime.utcnow)
class Notification(Base):
    __tablename__='notifications'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uid); user_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id')); match_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('matches.id')); title: Mapped[str]=mapped_column(String); body: Mapped[str]=mapped_column(Text); read: Mapped[bool]=mapped_column(Boolean,default=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
