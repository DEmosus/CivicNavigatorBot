from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime, timezone

from backend.db import get_session
from backend.utils.helpers import generate_public_id
from backend.models import Conversation, Message, Sender, KBDoc, Incident, IncidentStatus
from backend.schemas import ChatIn, ChatOut, Citation
from backend.utils.search import score_text, best_snippet
from backend.utils.intent import IntentClassifier

router = APIRouter(prefix="/api/chat", tags=["chat"])

classifier = IntentClassifier()


@router.post("/message", response_model=ChatOut)
async def chat_message(payload: ChatIn, session: Session = Depends(get_session)):
    session_id = payload.session_id or str(uuid4())

    # === 1. Find or create conversation ===
    convo = session.exec(select(Conversation).where(Conversation.session_id == session_id)).first()
    if not convo:
        convo = Conversation(session_id=session_id, user_id=None, pending_intent=None, state={})
        session.add(convo)
        session.flush()

    # === 2. Save user message ===
    msg_user = Message(
        conversation_id=convo.id,
        sender=payload.role or Sender.resident,
        text=payload.message,
    )
    session.add(msg_user)

    reply = ""
    confidence = 0.5
    citations: list[Citation] = []

    # Ensure convo.state dict exists
    if convo.state is None:
        convo.state = {}

    # === 3. Handle pending intent (multi-turn state machine) ===
    if convo.pending_intent == "incident_report_flow":
        step = convo.state.get("step", "title")

        if step == "title":
            convo.state = {**convo.state, "title": payload.message, "step": "category"}
            reply = "Got it. What’s the category (e.g. streetlight, water, road, trash)?"

        elif step == "category":
            convo.state = {**convo.state, "category": payload.message, "step": "location"}
            reply = "Noted. Can you provide the exact location or nearest landmark?"

        elif step == "location":
            convo.state = {**convo.state, "location_text": payload.message, "step": "email"}
            reply = "Thanks. Could I have your contact email in case staff need more info?"

        elif step == "email":
            convo.state = {**convo.state, "email": payload.message, "step": "description"}
            reply = "Finally, please add a short description."

        elif step == "description":
            convo.state = {**convo.state, "description": payload.message}

            # Save incident
            incident = Incident(
                public_id=generate_public_id(),
                title=convo.state.get("title") or "No Title",
                category=convo.state.get("category") or "other",
                location_text=convo.state.get("location_text"),
                contact_email=convo.state.get("email"),
                description=convo.state.get("description") or "",
                status=IncidentStatus.open,
                created_at=datetime.now(timezone.utc),
            )
            session.add(incident)

            reply = (
                f"✅ Thanks, I’ve filed your incident report: *{incident.title}*.\n"
                f"Your incident ID is **{incident.public_id}**. We’ll update you when the status changes."
            )
            convo.pending_intent = None
            convo.state = {}
            confidence = 0.95

    elif convo.pending_intent == "incident_report_choice":
        choice = payload.message.strip().lower()
        if "chat" in choice:
            reply = "Great — let’s file it here. What’s the title of this report?"
            convo.pending_intent = "incident_report_flow"
            convo.state = {"step": "title"}
        elif "form" in choice:
            reply = "Okay, opening the incident form for you…"
            convo.pending_intent = None
            convo.state = {}
        else:
            reply = "Would you like to file this in chat, or open the incident form?"

    elif convo.pending_intent == "status_check":
        # User should provide an incident ID
        incident = session.exec(select(Incident).where(Incident.public_id == payload.message.strip())).first()
        if incident:
            reply = f"ℹ️ The status of incident **{incident.public_id}** is: *{incident.status.value}*."
        else:
            reply = "❌ Sorry, I couldn’t find an incident with that ID. Please double-check."
        convo.pending_intent = None
        confidence = 0.9

    else:
        # === 4. Detect intent on fresh message ===
        intent, intent_conf = await classifier.classify_intent(payload.message)
        confidence = intent_conf

        if intent == "incident_report":
            reply = "Would you like to file this in chat, or open the incident form?"
            convo.pending_intent = "incident_report_choice"

        elif intent == "status_check":
            reply = "Sure — can you provide the incident ID so I can check its status?"
            convo.pending_intent = "status_check"

        elif intent == "general_query":
            # === Knowledge base search ===
            docs = session.exec(select(KBDoc)).all()
            scored = [(d, score_text(payload.message, f"{d.title}\n{d.body}")) for d in docs]
            scored = [t for t in scored if t[1] > 0]
            scored.sort(key=lambda x: x[1], reverse=True)
            top = scored[:3]

            citations = [
                Citation(title=d.title, snippet=best_snippet(d.body, payload.message), source_link=d.source_url)
                for d, _ in top
            ]

            if top:
                reply = "Here’s what I found:\n" + "\n".join(
                    f"{i+1}. {c.title}" for i, c in enumerate(citations)
                )
                confidence = 0.75 if len(top) >= 2 else 0.55
            else:
                reply = "I couldn’t find a reliable answer in the KB. Could you clarify?"
                confidence = 0.2

        else:
            reply = "I’m not sure I understood. Could you clarify?"

    # === 5. Save bot reply ===
    msg_bot = Message(
        conversation_id=convo.id,
        sender=Sender.bot,
        text=reply,
    )
    session.add(msg_bot)
    session.commit()

    return ChatOut(
        reply=reply,
        citations=citations,
        confidence=confidence,
        session_id=session_id,
    )
