
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

function EventDetails() {
    const { eventId } = useParams();

    const [event, setEvent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        getEvent();
    }, [eventId]);

    const getEvent = async () => {
        try {
            const response = await axios.get(
                `http://127.0.0.1:8000/events/${eventId}`
            );

            setEvent(response.data);
            setError("");
        } catch (err) {
            console.error(err);

            setError(
                "Unable to load event details."
            );
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="event-details">
                <div className="status-message">
                    Loading event details...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="event-details">

                <div className="status-message error-message">
                    {error}
                </div>

                <Link
                    to="/"
                    className="back-link"
                >
                    Back to Events
                </Link>

            </div>
        );
    }

    if (!event) {
        return null;
    }

    return (
        <div className="event-details">

            <Link
                to="/"
                className="back-link"
            >
                Back to Events
            </Link>

            <div className="details-card">

                {/* EVENT IMAGE */}

                {event.banner_image ? (
                    <div className="event-image-container">

                        <img
                            src={event.banner_image}
                            alt={event.title}
                            className="event-image"
                        />

                    </div>
                ) : (
                    <div className="no-image">
                        No event image available
                    </div>
                )}

                {/* EVENT INFORMATION */}

                <div className="details-content">

                    <span className="event-category">
                        {event.category}
                    </span>

                    <h1>
                        {event.title}
                    </h1>

                    <div className="description-section">

                        <h3>
                            About this event
                        </h3>

                        <p>
                            {event.description}
                        </p>

                    </div>

                    <div className="event-details-grid">

                        <div className="detail-item">

                            <span className="detail-label">
                                Location
                            </span>

                            <strong>
                                {event.location}
                            </strong>

                        </div>

                        <div className="detail-item">

                            <span className="detail-label">
                                Date & Time
                            </span>

                            <strong>
                                {new Date(
                                    event.event_date
                                ).toLocaleString()}
                            </strong>

                        </div>

                        <div className="detail-item">

                            <span className="detail-label">
                                Ticket Price
                            </span>

                            <strong className="detail-price">
                                ₹{event.ticket_price}
                            </strong>

                        </div>

                        <div className="detail-item">

                            <span className="detail-label">
                                Available Tickets
                            </span>

                            <strong>
                                {event.available_tickets}
                            </strong>

                        </div>

                    </div>

                    {/* BOOK BUTTON */}

                    {event.available_tickets > 0 ? (

                        <Link
                            to={`/book/${event.id}`}
                            className="book-event-button"
                        >
                            Book Ticket
                        </Link>

                    ) : (

                        <div className="sold-out-message">
                            Sold Out
                        </div>

                    )}

                </div>

            </div>

        </div>
    );
}

export default EventDetails;
