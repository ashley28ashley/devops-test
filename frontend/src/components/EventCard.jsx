import { Link } from "react-router-dom";
import "./EventCard.css";

export default function EventCard({ event }) {
  return (
    <div className="event-card">
      <h3>{event.title}</h3>

      {/* Adresse */}
      <p>
        {event.address_street
          ? `${event.address_street}, ${event.city_name || ""}`
          : event.city_name || "Lieu non renseigné"}
      </p>

      {/* Date */}
      <p>
        {event.event_date
          ? new Date(event.event_date).toLocaleDateString("fr-FR")
          : "Date non renseignée"}
      </p>

      <Link to={`/events/${event.id}`} className="detail-btn">
        Voir détail
      </Link>
    </div>
  );
}