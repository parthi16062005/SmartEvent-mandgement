
import os
import uuid
import qrcode

from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import models
from database import engine, get_db

from schemas import (
    UserRegister,
    UserResponse,
    TokenResponse,
    EventCreate,
    EventResponse,
    BookingCreate,
    BookingResponse,
    BookingHistoryResponse,
    TicketResponse,
    NotificationResponse
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_id_from_token
)


# =========================
# DATABASE
# =========================

models.Base.metadata.create_all(bind=engine)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="SmartEvent - Event Discovery & Ticket Booking System",
    description="SmartEvent API for event discovery and ticket booking",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# OAUTH2
# =========================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# =========================
# QR TICKET STORAGE
# =========================

TICKETS_DIR = "tickets"

os.makedirs(
    TICKETS_DIR,
    exist_ok=True
)

app.mount(
    "/tickets",
    StaticFiles(directory=TICKETS_DIR),
    name="tickets"
)


# =========================
# ROOT
# =========================

@app.get(
    "/",
    tags=["Root"]
)
def root():
    return {
        "message": "SmartEvent API is running"
    }


# =========================
# AUTHENTICATION
# =========================

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    existing_username = (
        db.query(models.User)
        .filter(
            models.User.username == user.username
        )
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = (
        db.query(models.User)
        .filter(
            models.User.email == user.email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/login",
    response_model=TokenResponse,
    tags=["Authentication"]
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(
            models.User.email == form_data.username
        )
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        existing_user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(
        token
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = (
        db.query(models.User)
        .filter(
            models.User.id == user_id
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@app.get(
    "/profile",
    response_model=UserResponse,
    tags=["Authentication"]
)
def profile(
    current_user: models.User = Depends(
        get_current_user
    )
):
    return current_user


# =========================
# EVENT DISCOVERY
# =========================

@app.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"]
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    new_event = models.Event(
        title=event.title,
        description=event.description,
        category=event.category,
        location=event.location,
        event_date=event.event_date,
        ticket_price=event.ticket_price,
        banner_image=event.banner_image,
        total_tickets=event.total_tickets,
        available_tickets=event.total_tickets
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@app.get(
    "/events",
    response_model=list[EventResponse],
    tags=["Events"]
)
def get_events(
    category: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        models.Event
    )

    if category:
        query = query.filter(
            models.Event.category.ilike(
                category
            )
        )

    if search:
        search_text = f"%{search}%"

        query = query.filter(
            models.Event.title.ilike(
                search_text
            )
        )

    events = (
        query
        .order_by(
            models.Event.event_date
        )
        .all()
    )

    return events


@app.get(
    "/events/{event_id}",
    response_model=EventResponse,
    tags=["Events"]
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(models.Event)
        .filter(
            models.Event.id == event_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


# =========================
# TICKET BOOKING
# =========================

@app.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Bookings"]
)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    event = (
        db.query(models.Event)
        .filter(
            models.Event.id == booking.event_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if booking.ticket_quantity > event.available_tickets:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only {event.available_tickets} "
                "tickets are available"
            )
        )

    total_price = (
        event.ticket_price
        * booking.ticket_quantity
    )

    new_booking = models.Booking(
        user_id=current_user.id,
        event_id=event.id,
        ticket_quantity=booking.ticket_quantity,
        total_price=total_price,
        booking_status="CONFIRMED"
    )

    event.available_tickets -= (
        booking.ticket_quantity
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    new_notification = models.Notification(
        user_id=current_user.id,
        title="Booking Confirmed",
        message=(
            f"Your booking for {event.title} "
            f"has been confirmed. "
            f"Ticket quantity: {booking.ticket_quantity}."
        ),
        type="BOOKING",
        is_read=False
    )

    db.add(new_notification)
    db.commit()

    return new_booking


@app.get(
    "/bookings",
    response_model=list[BookingHistoryResponse],
    tags=["Bookings"]
)
def get_booking_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    bookings = (
        db.query(models.Booking)
        .filter(
            models.Booking.user_id
            == current_user.id
        )
        .order_by(
            models.Booking.created_at.desc()
        )
        .all()
    )

    history = []

    for booking in bookings:
        history.append(
            BookingHistoryResponse(
                id=booking.id,
                event_id=booking.event_id,
                event_title=booking.event.title,
                ticket_quantity=booking.ticket_quantity,
                total_price=booking.total_price,
                booking_status=booking.booking_status,
                created_at=booking.created_at
            )
        )

    return history


# =========================
# CANCEL BOOKING
# =========================

@app.post(
    "/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    tags=["Bookings"]
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.id == booking_id,
            models.Booking.user_id
            == current_user.id
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.booking_status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Booking is already cancelled"
        )

    booking.booking_status = "CANCELLED"

    event = (
        db.query(models.Event)
        .filter(
            models.Event.id
            == booking.event_id
        )
        .first()
    )

    if event:
        event.available_tickets += (
            booking.ticket_quantity
        )

        if (
            event.available_tickets
            > event.total_tickets
        ):
            event.available_tickets = (
                event.total_tickets
            )

    db.commit()
    db.refresh(booking)

    return booking


# =========================
# QR CODE TICKET
# =========================

@app.post(
    "/bookings/{booking_id}/ticket",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tickets"]
)
def generate_ticket(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.id == booking_id,
            models.Booking.user_id
            == current_user.id
        )
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.booking_status != "CONFIRMED":
        raise HTTPException(
            status_code=400,
            detail=(
                "QR ticket can only be generated "
                "for confirmed bookings"
            )
        )

    existing_ticket = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.booking_id
            == booking.id
        )
        .first()
    )

    if existing_ticket:
        return existing_ticket

    ticket_code = (
        "TKT-"
        + uuid.uuid4().hex[:12].upper()
    )

    qr_data = (
        f"SmartEvent Ticket\n"
        f"Ticket Code: {ticket_code}\n"
        f"Booking ID: {booking.id}\n"
        f"Event ID: {booking.event_id}"
    )

    qr = qrcode.make(
        qr_data
    )

    filename = (
        f"{ticket_code}.png"
    )

    filepath = os.path.join(
        TICKETS_DIR,
        filename
    )

    qr.save(filepath)

    qr_code_url = (
        f"/tickets/{filename}"
    )

    new_ticket = models.Ticket(
        booking_id=booking.id,
        ticket_code=ticket_code,
        qr_code_url=qr_code_url
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


# =========================
# VERIFY QR TICKET
# =========================

@app.get(
    "/verify-ticket/{ticket_code}",
    tags=["Tickets"]
)
def verify_ticket(
    ticket_code: str,
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.ticket_code
            == ticket_code
        )
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid ticket"
        )

    booking = ticket.booking

    if booking.booking_status != "CONFIRMED":
        return {
            "valid": False,
            "ticket_code": ticket.ticket_code,
            "booking_id": booking.id,
            "event_id": booking.event_id,
            "booking_status": booking.booking_status,
            "message": "Ticket is not valid"
        }

    return {
        "valid": True,
        "ticket_code": ticket.ticket_code,
        "booking_id": booking.id,
        "event_id": booking.event_id,
        "booking_status": booking.booking_status,
        "message": "Ticket is valid"
    }


# =========================
# NOTIFICATIONS
# =========================

@app.get(
    "/notifications",
    response_model=list[NotificationResponse],
    tags=["Notifications"]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    notifications = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id
            == current_user.id
        )
        .order_by(
            models.Notification.created_at.desc()
        )
        .all()
    )

    return notifications


# =========================
# UNREAD NOTIFICATION COUNT
# =========================

@app.get(
    "/notifications/unread-count",
    tags=["Notifications"]
)
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    unread_count = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id
            == current_user.id,
            models.Notification.is_read == False
        )
        .count()
    )

    return {
        "unread_count": unread_count
    }


# =========================
# MARK NOTIFICATION AS READ
# =========================

@app.post(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    tags=["Notifications"]
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id
            == notification_id,
            models.Notification.user_id
            == current_user.id
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


# =========================
# CREATE EVENT REMINDERS
# =========================

@app.post(
    "/notifications/create-reminders",
    tags=["Notifications"]
)
def create_event_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    )
):
    now = datetime.now(timezone.utc)

    reminder_limit = now + timedelta(
        hours=24
    )

    upcoming_events = (
        db.query(models.Event)
        .filter(
            models.Event.event_date >= now,
            models.Event.event_date <= reminder_limit
        )
        .all()
    )

    reminders_created = 0

    for event in upcoming_events:

        booking = (
            db.query(models.Booking)
            .filter(
                models.Booking.event_id == event.id,
                models.Booking.user_id == current_user.id,
                models.Booking.booking_status == "CONFIRMED"
            )
            .first()
        )

        if booking is None:
            continue

        existing_reminder = (
            db.query(models.Notification)
            .filter(
                models.Notification.user_id
                == current_user.id,
                models.Notification.type
                == "EVENT",
                models.Notification.title
                == "Event Reminder",
                models.Notification.message.contains(
                    event.title
                )
            )
            .first()
        )

        if existing_reminder:
            continue

        reminder = models.Notification(
            user_id=current_user.id,
            title="Event Reminder",
            message=(
                f"Your event {event.title} "
                f"is scheduled within the next 24 hours."
            ),
            type="EVENT",
            is_read=False
        )

        db.add(reminder)
        reminders_created += 1

    db.commit()

    return {
        "message": "Event reminders checked",
        "reminders_created": reminders_created
    }
