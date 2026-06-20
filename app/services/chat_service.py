import json
import random
import os
from typing import List, Dict, Optional

# Path to intents.json (inside app/data/)
INTENTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "intents.json"
)


def load_intents():
    try:
        with open(INTENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("intents", [])
    except Exception as e:
        print(f"Error loading intents.json: {e}")
        return []


INTENTS = load_intents()


def extract_name(message: str) -> Optional[str]:
    msg_lower = message.lower().strip()

    # "i am John", "my name is John", "this is John" patterns
    patterns = [
        r"i am ([a-zA-Z]+)",
        r"i'm ([a-zA-Z]+)",
        r"my name is ([a-zA-Z]+)",
        r"this is ([a-zA-Z]+)",
        r"myself ([a-zA-Z]+)",
        r"it's ([a-zA-Z]+)",
        r"its ([a-zA-Z]+)",
        r"call me ([a-zA-Z]+)",
        r"named ([a-zA-Z]+)",
    ]

    import re

    for pattern in patterns:
        match = re.search(pattern, msg_lower)
        if match:
            name = match.group(1).capitalize()
            # Common words skip பண்ணு (not a name)
            skip_words = [
                "here",
                "there",
                "fine",
                "good",
                "ok",
                "okay",
                "not",
                "new",
                "back",
                "home",
                "ready",
                "the",
                "a",
            ]
            if name.lower() not in skip_words:
                return name
    return None


def match_intent(message: str) -> Optional[str]:
    msg_lower = message.lower().strip()
    for intent in INTENTS:
        for pattern in intent.get("patterns", []):
            pattern_lower = pattern.lower()
            if pattern_lower in msg_lower or msg_lower in pattern_lower:
                responses = intent.get("responses", [])
                if responses:
                    return random.choice(responses)
    return None


def find_best_faq_reply(message: str, faqs: List[Dict[str, str]]) -> Optional[str]:
    msg_lower = message.lower().strip()
    for faq in faqs:
        q = faq.get("question", "").lower()
        if q and (q in msg_lower or msg_lower in q):
            return faq.get("answer")
    return None


# def get_reply_from_chatbot(
#     message: str, faqs: List[Dict], welcome_message: str = None
# ) -> str:
#     # 1. Try intents
#     intent_reply = match_intent(message)
#     if intent_reply:
#         return intent_reply
#     # 2. Try custom FAQs
#     faq_reply = find_best_faq_reply(message, faqs)
#     if faq_reply:
#         return faq_reply
#     # 3. Fallback
#     if welcome_message:
#         return welcome_message
#     return "Thank you for your query. Our team will contact you shortly."


def get_reply_from_chatbot(
    message: str, faqs: List[Dict], welcome_message: str = None
) -> str:

    # 0. Name extract check
    name = extract_name(message)
    if name:
        return (
            f"Hello {name}! 👋 Welcome to Wyn Message Tool! How can I help you today?"
        )

    # 1. Try intents
    intent_reply = match_intent(message)
    if intent_reply:
        return intent_reply

    # 2. Try custom FAQs
    faq_reply = find_best_faq_reply(message, faqs)
    if faq_reply:
        return faq_reply

    # 3. Fallback
    if welcome_message:
        return welcome_message
    return "Thank you for your query. Our team will contact you shortly."
