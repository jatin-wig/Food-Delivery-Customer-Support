from database import SessionLocal, Order
from datetime import datetime, timezone


def create_order(user_id, item, price):

    db = SessionLocal()

    order = Order(
        user_id=user_id,
        item=item,
        price=price,
        status="PLACED",
        eta="25 mins",
        created_at=datetime.now(timezone.utc)
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()

    return order



def compute_status(order):

    now = datetime.now(timezone.utc)
    created = order.created_at

    if created is None:
        created = now

    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)

    seconds = (now - created).total_seconds()
    total_delivery_seconds = 600
    remaining = max(0, int(total_delivery_seconds - seconds))

    if order.status == "CANCELLED":
        return "CANCELLED", "N/A"

    if remaining <= 0:
        return "DELIVERED", "Delivered"

    minutes = remaining // 60
    seconds_left = remaining % 60
    eta = f"{minutes:02d}:{seconds_left:02d}"

    if seconds < 120:
        return "PLACED", eta

    elif seconds < 300:
        return "PREPARING", eta

    elif seconds < 600:
        return "OUT_FOR_DELIVERY", eta

    else:
        return "DELIVERED", "Delivered"




def get_latest_order(user_id):

    db = SessionLocal()

    order = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .first()
    )

    if not order:
        db.close()
        return None

    status, eta = compute_status(order)

    order.status = status
    order.eta = eta

    db.commit()
    db.refresh(order)
    db.close()

    return order


def cancel_order(order_id):

    db = SessionLocal()

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        db.close()
        return None

    if order.status == "DELIVERED":
        db.close()
        return None

    order.status = "CANCELLED"
    order.eta = "N/A"

    db.commit()
    db.refresh(order)
    db.close()

    return order


def update_order_status(order_id, status, eta=None):

    db = SessionLocal()

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        db.close()
        return None

    order.status = status

    if eta is not None:
        order.eta = eta

    db.commit()
    db.refresh(order)
    db.close()

    return order
