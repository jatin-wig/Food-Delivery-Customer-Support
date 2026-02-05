from database import SessionLocal, Ticket


def create_ticket(user_id, order_id, intent, history):

    db = SessionLocal()

    existing = (
        db.query(Ticket)
        .filter(
            Ticket.order_id == order_id,
            Ticket.status == "OPEN"
        )
        .first()
    )

    if existing:
        db.close()
        return existing.id

    ticket = Ticket(
        user_id=user_id,
        order_id=order_id,
        issue_type=intent,
        conversation="\n".join(history),
        status="OPEN"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()

    return ticket.id


def close_ticket(ticket_id):

    db = SessionLocal()

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        db.close()
        return None

    ticket.status = "CLOSED"

    db.commit()
    db.refresh(ticket)
    db.close()

    return ticket


def get_all_tickets():

    db = SessionLocal()

    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()

    db.close()

    return tickets


def get_open_tickets():

    db = SessionLocal()

    tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "OPEN")
        .order_by(Ticket.id.desc())
        .all()
    )

    db.close()

    return tickets
