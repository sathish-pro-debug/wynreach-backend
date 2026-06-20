# # from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
# # from sqlalchemy.sql import func
# # from app.database import Base   # ✅ use Base from main DB

# # class Chatbot(Base):
# #     __tablename__ = "chatbots"

# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String, nullable=False)
# #     description = Column(String, nullable=True)
# #     status = Column(String, default="active")
# #     welcome_message = Column(String, default="Hi! Welcome to our service. How can I help you today?")
# #     buttons = Column(JSON, default=list)
# #     faqs = Column(JSON, default=list)
# #     conversations = Column(Integer, default=0)
# #     satisfaction = Column(Float, default=0.0)
# #     responses = Column(Integer, default=0)
# #     last_active = Column(DateTime, default=func.now(), onupdate=func.now())
# #     created_at = Column(DateTime, server_default=func.now())
# #     updated_at = Column(DateTime, onupdate=func.now())



# from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# from app.database import Base

# class Chatbot(Base):
#     __tablename__ = "chatbots"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     status = Column(String, default="active")
#     welcome_message = Column(String, default="Hi! Welcome to our service. How can I help you today?")
#     buttons = Column(JSON, default=list)
#     faqs = Column(JSON, default=list)
#     conversations = Column(Integer, default=0)
#     satisfaction = Column(Float, default=0.0)
#     responses = Column(Integer, default=0)
#     last_active = Column(DateTime, default=func.now(), onupdate=func.now())
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, onupdate=func.now())

#     # Relationship
#     conversations_rel = relationship("ChatConversation", back_populates="chatbot")

# class ChatConversation(Base):
#     __tablename__ = "chat_conversations"

#     id = Column(Integer, primary_key=True, index=True)
#     chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
#     user_id = Column(Integer, nullable=True)          # if you have user auth
#     workspace_id = Column(String, nullable=True)      # from your screenshot
#     started_at = Column(DateTime, server_default=func.now())
#     ended_at = Column(DateTime, nullable=True)
#     message_count = Column(Integer, default=0)

#     # Relationship
#     chatbot = relationship("Chatbot", back_populates="conversations_rel")
#     messages = relationship("ChatMessage", back_populates="conversation")

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
#     role = Column(String, nullable=False)        # 'user' or 'bot'
#     content = Column(Text, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())

#     # Relationship
#     conversation = relationship("ChatConversation", back_populates="messages")


from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    welcome_message = Column(String, default="Hi! Welcome to our service. How can I help you today?")
    buttons = Column(JSON, default=list)
    faqs = Column(JSON, default=list)
    conversations = Column(Integer, default=0)
    satisfaction = Column(Float, default=0.0)
    responses = Column(Integer, default=0)
    last_active = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    conversation_records = relationship("ChatConversation", back_populates="chatbot")


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    user_id = Column(Integer, nullable=True)          # optional, for logged-in users
    workspace_id = Column(String, nullable=True)      # optional, from your screenshot
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)

    chatbot = relationship("Chatbot", back_populates="conversation_records")
    messages = relationship("ChatMessage", back_populates="conversation")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    role = Column(String, nullable=False)     # 'user' or 'bot'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("ChatConversation", back_populates="messages")