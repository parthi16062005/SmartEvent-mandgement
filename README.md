# SmartEvent – Event Discovery & Ticket Booking System

SmartEvent is a full-stack event discovery and ticket booking web application. Users can register, log in, search for events, filter events by category, book tickets, view booking history, receive notifications, and access QR-based tickets.

## Features

### Authentication

* User registration
* User login
* JWT authentication
* Protected user APIs
* User profile

### Event Discovery

* View upcoming events
* View event details
* Search events
* Filter events by category
* Event banner images
* Ticket price and availability

### Event Categories

* Tech
* Music
* Sports
* Business

### Ticket Booking

* Select ticket quantity
* Automatic total price calculation
* Ticket availability validation
* Booking confirmation
* Booking history
* Cancel booking

### QR Ticket

* Generate unique ticket code
* Generate QR code after successful booking
* Display QR ticket
* Verify ticket using ticket code

### Notifications

* Booking confirmation notifications
* Event reminder notifications
* Notification list
* Unread notification count
* Mark notifications as read

## Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* JWT Authentication
* Bcrypt Password Hashing
* QR Code Generation
* Pytest

### Frontend

* React
* Vite
* React Router
* Axios
* Lucide React
* CSS

## Project Structure

```text
SmartEvent/
│
├── backend/
│   ├── venv/
│   ├── tickets/
│   ├── tests/
│   │   └── test_api.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── main.py
│
├── frontend/
│   ├── node_modules/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── EventDetails.jsx
│   │   │   ├── Booking.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── BookingSuccess.jsx
│   │   │   └── BookingHistory.jsx
│   │   ├── styles/
│   │   │   └── App.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── index.html
│   └── vite.config.js
│
└── README.md
```

## Backend Setup

Open PowerShell and run:

```powershell
cd "C:\Users\parth\OneDrive\Desktop\SmartEvent\backend"
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Start the FastAPI server:

```powershell
python -m uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another PowerShell terminal:

```powershell
cd "C:\Users\parth\OneDrive\Desktop\SmartEvent\frontend"
```

Install dependencies if required:

```powershell
npm install
```

Start the React application:

```powershell
npm run dev
```

Frontend will normally run at:

```text
http://localhost:5173
```

## Testing

The backend contains automated API tests using Pytest.

Run:

```powershell
cd "C:\Users\parth\OneDrive\Desktop\SmartEvent\backend"
.\venv\Scripts\Activate.ps1
python -m pytest -v
```

Current test result:

```text
8 passed
```

The tests cover:

* Event listing
* Event details
* Unauthorized profile access
* Unauthorized booking access
* Unauthorized notification access
* Unauthorized unread notification access
* Invalid ticket verification
* Invalid login

## Main API Endpoints

| Method | Endpoint                                | Purpose                    |
| ------ | --------------------------------------- | -------------------------- |
| POST   | `/register`                             | Register a user            |
| POST   | `/login`                                | User login                 |
| GET    | `/profile`                              | Get logged-in user profile |
| POST   | `/events`                               | Create an event            |
| GET    | `/events`                               | Get events                 |
| GET    | `/events/{event_id}`                    | Get event details          |
| POST   | `/bookings`                             | Create booking             |
| GET    | `/bookings`                             | Get booking history        |
| POST   | `/bookings/{booking_id}/cancel`         | Cancel booking             |
| POST   | `/bookings/{booking_id}/ticket`         | Generate QR ticket         |
| GET    | `/verify-ticket/{ticket_code}`          | Verify QR ticket           |
| GET    | `/notifications`                        | Get notifications          |
| GET    | `/notifications/unread-count`           | Get unread count           |
| POST   | `/notifications/{notification_id}/read` | Mark notification as read  |
| POST   | `/notifications/create-reminders`       | Create event reminders     |

## Booking Flow

```text
Register
   ↓
Login
   ↓
Browse Events
   ↓
Search / Filter Category
   ↓
View Event Details
   ↓
Select Ticket Quantity
   ↓
Book Ticket
   ↓
Booking Confirmation
   ↓
Generate QR Ticket
   ↓
View Booking History
   ↓
Verify Ticket
```

## Notification Flow

```text
Booking Confirmed
       ↓
Notification Created
       ↓
Notification Bell
       ↓
Unread Count
       ↓
Open Notification
       ↓
Mark as Read
```

## Production Build

To create the frontend production build:

```powershell
cd "C:\Users\parth\OneDrive\Desktop\SmartEvent\frontend"
npm run build
```

The project successfully builds for production.

## Future Improvements

* Online payment integration
* Admin dashboard
* Event organizer management
* Email notifications
* Advanced event filtering
* Deployment to cloud hosting
* Mobile application

## Conclusion

SmartEvent provides a complete event discovery and ticket booking experience with secure authentication, event management, ticket booking, QR-based ticket verification, booking history, and notifications.

The project demonstrates the integration of a FastAPI backend with a React frontend and a SQL database to build a practical full-stack web application.
