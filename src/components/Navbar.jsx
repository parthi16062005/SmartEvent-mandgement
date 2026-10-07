
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bell } from "lucide-react";
import axios from "axios";

function Navbar() {
    const [searchText, setSearchText] = useState("");

    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [showNotifications, setShowNotifications] = useState(false);

    const navigate = useNavigate();

    const handleSearch = () => {
        const searchValue = searchText.trim();

        if (searchValue) {
            navigate(
                `/?search=${encodeURIComponent(searchValue)}`
            );
        } else {
            navigate("/");
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            handleSearch();
        }
    };

    const getNotifications = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            return;
        }

        try {
            const response = await axios.get(
                "http://127.0.0.1:8000/notifications",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setNotifications(response.data);
        } catch (error) {
            console.error(
                "Unable to load notifications:",
                error
            );
        }
    };

    const getUnreadCount = async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            return;
        }

        try {
            const response = await axios.get(
                "http://127.0.0.1:8000/notifications/unread-count",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setUnreadCount(
                response.data.unread_count
            );
        } catch (error) {
            console.error(
                "Unable to load unread count:",
                error
            );
        }
    };

    useEffect(() => {
        getNotifications();
        getUnreadCount();
    }, []);

    const handleNotificationClick = async (
        notification
    ) => {
        const token = localStorage.getItem(
            "access_token"
        );

        if (!token) {
            return;
        }

        if (!notification.is_read) {
            try {
                const response = await axios.post(
                    `http://127.0.0.1:8000/notifications/${notification.id}/read`,
                    {},
                    {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    }
                );

                setNotifications(
                    (currentNotifications) =>
                        currentNotifications.map(
                            (item) =>
                                item.id === notification.id
                                    ? response.data
                                    : item
                        )
                );

                setUnreadCount(
                    (count) =>
                        count > 0 ? count - 1 : 0
                );
            } catch (error) {
                console.error(
                    "Unable to mark notification as read:",
                    error
                );
            }
        }
    };

    const toggleNotifications = () => {
        setShowNotifications(
            !showNotifications
        );

        if (!showNotifications) {
            getNotifications();
            getUnreadCount();
        }
    };

    return (
        <header className="navbar">
            <div className="navbar-container">

                <Link
                    to="/"
                    className="navbar-brand"
                >
                    SmartEvent
                </Link>

                <nav className="navbar-links">

                    <Link to="/">
                        Home
                    </Link>

                    <a href="/#categories">
                        Categories
                    </a>

                    <Link to="/bookings">
                        My Bookings
                    </Link>

                </nav>

                <div className="navbar-search">

                    <input
                        type="text"
                        placeholder="Search events..."
                        value={searchText}
                        onChange={(event) =>
                            setSearchText(
                                event.target.value
                            )
                        }
                        onKeyDown={handleKeyDown}
                    />

                    <button
                        type="button"
                        onClick={handleSearch}
                    >
                        Search
                    </button>

                </div>

                <div className="navbar-actions">

                    <div className="notification-wrapper">

                        <button
                            type="button"
                            className="notification-button"
                            onClick={
                                toggleNotifications
                            }
                            aria-label="Notifications"
                        >
                            <Bell
                                size={21}
                                strokeWidth={2}
                            />

                            {unreadCount > 0 && (
                                <span className="notification-count">
                                    {unreadCount}
                                </span>
                            )}
                        </button>

                        {showNotifications && (
                            <div className="notification-dropdown">

                                <div className="notification-header">

                                    <strong>
                                        Notifications
                                    </strong>

                                    <span>
                                        {unreadCount} unread
                                    </span>

                                </div>

                                <div className="notification-list">

                                    {notifications.length === 0 ? (

                                        <div className="no-notifications">
                                            No notifications
                                        </div>

                                    ) : (

                                        notifications.map(
                                            (notification) => (

                                                <button
                                                    type="button"
                                                    key={
                                                        notification.id
                                                    }
                                                    className={`notification-item ${
                                                        notification.is_read
                                                            ? "read"
                                                            : "unread"
                                                    }`}
                                                    onClick={() =>
                                                        handleNotificationClick(
                                                            notification
                                                        )
                                                    }
                                                >

                                                    <div className="notification-title">
                                                        {
                                                            notification.title
                                                        }
                                                    </div>

                                                    <div className="notification-message">
                                                        {
                                                            notification.message
                                                        }
                                                    </div>

                                                    <div className="notification-date">
                                                        {new Date(
                                                            notification.created_at
                                                        ).toLocaleString()}
                                                    </div>

                                                </button>

                                            )
                                        )

                                    )}

                                </div>

                            </div>
                        )}

                    </div>

                    <Link
                        to="/login"
                        className="login-button"
                    >
                        Login
                    </Link>

                    <Link
                        to="/register"
                        className="register-button"
                    >
                        Register
                    </Link>

                </div>

            </div>
        </header>
    );
}

export default Navbar;
