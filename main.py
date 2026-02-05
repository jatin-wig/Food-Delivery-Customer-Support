from fastapi import FastAPI
from pydantic import BaseModel

from llm import detect_intent, chat_reply
from sessions import get_session
from orders import create_order, get_latest_order, cancel_order, update_order_status

app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


class OrderRequest(BaseModel):
    user_id: str
    item: str
    price: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/create-order")
def create_new_order(req: OrderRequest):

    order = create_order(
        req.user_id,
        req.item,
        req.price
    )

    return {
        "order_id": order.id,
        "item": order.item,
        "price": order.price,
        "status": order.status,
        "eta": order.eta,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }


@app.get("/latest-order/{user_id}")
def latest_order_endpoint(user_id: str):

    order = get_latest_order(user_id)

    if not order:
        return {}

    return {
        "order_id": order.id,
        "item": order.item,
        "price": order.price,
        "status": order.status,
        "eta": order.eta,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }


@app.post("/cancel-order/{order_id}")
def cancel_order_endpoint(order_id: int):

    order = cancel_order(order_id)

    if not order:
        return {}

    return {
        "order_id": order.id,
        "item": order.item,
        "price": order.price,
        "status": order.status,
        "eta": order.eta,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }



@app.post("/reactivate-order/{order_id}")
def reactivate_order_endpoint(order_id: int):
    # Reactivate a previously cancelled order
    order = update_order_status(order_id, "PLACED", eta="25 mins")

    if not order:
        return {}

    return {
        "order_id": order.id,
        "item": order.item,
        "price": order.price,
        "status": order.status,
        "eta": order.eta,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):

    user_id = request.user_id
    message = request.message
    msg = message.lower()

    order = get_latest_order(user_id)

    if not order:
        return ChatResponse(
            reply="No active order found. Please place an order first."
        )

    # -------- DETERMINISTIC EXECUTION LAYER --------

    if "where" in msg or "status" in msg:
        return ChatResponse(
            reply=f"Order #{order.id} is currently {order.status}. ETA: {order.eta}."
        )

    if "cancel" in msg:

        if order.status == "CANCELLED":
            return ChatResponse(
                reply=f"Order #{order.id} is already cancelled."
            )

        cancelled = cancel_order(order.id)

        if not cancelled:
            return ChatResponse(
                reply=f"Order #{order.id} could not be cancelled. It may already be delivered."
            )

        return ChatResponse(
            reply=f"Your order #{cancelled.id} has been cancelled successfully."
        )

    if "wrong" in msg or "refund" in msg:
        return ChatResponse(
            reply=f"I'm sorry about that. I've initiated a refund for order #{order.id}. The amount will reflect within 3-5 business days."
        )

    if msg in ["help", "support"]:
        return ChatResponse(
            reply=f"You have an active order #{order.id} for {order.item}. Ask me about delivery status, cancellations, or refunds."
        )

    # -------- LLM LAYER (ONLY WHEN NEEDED) --------

    session = get_session(user_id)

    session["history"].append(f"User: {message}")

    context = f"""
You are a smart food delivery support agent.

ACTIVE ORDER:
Order ID: {order.id}
Item: {order.item}
Status: {order.status}
ETA: {order.eta}

Never ask for information already available above.
Avoid generic support phrases.

Conversation:
{chr(10).join(session["history"])}
"""

    reply = chat_reply(context)

    session["history"].append(f"Assistant: {reply}")

    return ChatResponse(reply=reply)
