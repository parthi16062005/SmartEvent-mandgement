
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import axios from "axios";

function Home() {
    const [events, setEvents] = useState([]);
    const [filteredEvents, setFilteredEvents] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [selectedCategory, setSelectedCategory] = useState("");

    const [searchParams] = useSearchParams();

    const searchText = searchParams.get("search") || "";

    useEffect(() => {
        getEvents();
    }, []);

    useEffect(() => {
        filterEvents(searchText, selectedCategory);
    }, [events, searchText, selectedCategory]);

    const getEvents = async () => {
        try {
            const response = await axios.get(
                "http://127.0.0.1:8000/events"
            );

            setEvents(response.data);
            setError("");
        } catch (err) {
            console.error(err);

            setError(
                "Unable to load events. Please make sure the FastAPI server is running."
            );
        } finally {
            setLoading(false);
        }
    };

    const filterEvents = (search, category) => {
        let result = [...events];

        const searchValue = search.trim().toLowerCase();

        if (searchValue) {
            result = result.filter((event) =>
                event.title
                    ?.toLowerCase()
                    .includes(searchValue) ||

                event.description
                    ?.toLowerCase()
                    .includes(searchValue) ||

                event.location
                    ?.toLowerCase()
                    .includes(searchValue) ||

                event.category
                    ?.toLowerCase()
                    .includes(searchValue)
            );
        }

        if (category) {
            result = result.filter(
                (event) =>
                    event.category?.toLowerCase() ===
                    category.toLowerCase()
            );
        }

        setFilteredEvents(result);
    };

    const categories = [
        ...new Set(
            events
                .map((event) => event.category)
                .filter(Boolean)
        )
    ];

    const clearFilters = () => {
        setSelectedCategory("");
        window.history.pushState({}, "", "/");
        window.location.reload();
    };

    return (
        <div className="home">

            {/* HERO SECTION */}

            <section className="hero">

                <div className="hero-content">

                    <h1>
                        Discover Amazing Events
                    </h1>

                    <p>
                        Find events, book tickets and manage
                        your bookings easily with SmartEvent.
                    </p>

                </div>

            </section>


            {/* EVENTS SECTION */}

            <section
                className="events-section"
                id="categories"
            >

                <div className="section-header">

                    <h2>
                        Upcoming Events
                    </h2>

                    <p>
                        Explore upcoming events and book
                        your tickets today.
                    </p>

                </div>


                {/* CATEGORY FILTER */}

                {!loading &&
                    !error &&
                    categories.length > 0 && (

                        <div className="category-filter">

                            <button
                                type="button"
                                className={
                                    selectedCategory === ""
                                        ? "category-filter-button active"
                                        : "category-filter-button"
                                }
                                onClick={() =>
                                    setSelectedCategory("")
                                }
                            >
                                All
                            </button>


                            {categories.map((category) => (

                                <button
                                    type="button"
                                    key={category}
                                    className={
                                        selectedCategory === category
                                            ? "category-filter-button active"
                                            : "category-filter-button"
                                    }
                                    onClick={() =>
                                        setSelectedCategory(
                                            selectedCategory === category
                                                ? ""
                                                : category
                                        )
                                    }
                                >
                                    {category}
                                </button>

                            ))}

                        </div>

                    )}


                {/* ACTIVE SEARCH */}

                {searchText && !loading && !error && (

                    <div className="search-result-info">

                        Search results for:
                        <strong>
                            {" "}
                            "{searchText}"
                        </strong>

                    </div>

                )}


                {/* LOADING */}

                {loading && (
                    <div className="status-message">
                        Loading events...
                    </div>
                )}


                {/* ERROR */}

                {error && (
                    <div className="status-message error-message">
                        {error}
                    </div>
                )}


                {/* NO EVENTS */}

                {!loading &&
                    !error &&
                    filteredEvents.length === 0 && (

                        <div className="status-message">

                            <p>
                                No events found.
                            </p>

                            {searchText && (
                                <button
                                    type="button"
                                    onClick={clearFilters}
                                    className="clear-search-button"
                                >
                                    Clear Search
                                </button>
                            )}

                        </div>

                    )}


                {/* EVENTS */}

                {!loading &&
                    !error &&
                    filteredEvents.length > 0 && (

                        <div className="event-grid">

                            {filteredEvents.map((event) => (

                                <div
                                    className="event-card"
                                    key={event.id}
                                >

                                    <div className="event-card-content">

                                        <span className="event-category">
                                            {event.category}
                                        </span>


                                        <h3>
                                            {event.title}
                                        </h3>


                                        <p className="event-description">
                                            {event.description ||
                                                "Join this exciting event and enjoy an amazing experience."}
                                        </p>


                                        <div className="event-info">

                                            <p>
                                                <strong>
                                                    Location
                                                </strong>

                                                <span>
                                                    {event.location}
                                                </span>
                                            </p>


                                            <p>
                                                <strong>
                                                    Date
                                                </strong>

                                                <span>
                                                    {new Date(
                                                        event.event_date
                                                    ).toLocaleString()}
                                                </span>
                                            </p>


                                            <p>
                                                <strong>
                                                    Available Tickets
                                                </strong>

                                                <span>
                                                    {event.available_tickets}
                                                </span>
                                            </p>

                                        </div>


                                        <div className="event-card-footer">

                                            <span className="event-price">
                                                ₹{event.ticket_price}
                                            </span>


                                            <Link
                                                to={`/events/${event.id}`}
                                            >
                                                View Event
                                            </Link>

                                        </div>

                                    </div>

                                </div>

                            ))}

                        </div>

                    )}

            </section>

        </div>
    );
}

export default Home;
