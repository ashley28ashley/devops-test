import { useEffect, useState } from "react";
import { getEvents } from "../services/api";
import EventCard from "../components/EventCard";

export default function Events() {
  const [events, setEvents] = useState([]);
  const [filters, setFilters] = useState({
    title: "",
    location: "",
    dateMin: "",
    dateMax: ""
  });

  const [page, setPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    getEvents().then(setEvents);
  }, []);

  const filtered = events.filter(ev => {
    return (
      ev.title.toLowerCase().includes(filters.title.toLowerCase()) &&
      ev.location.toLowerCase().includes(filters.location.toLowerCase()) &&
      (!filters.dateMin || ev.date >= filters.dateMin) &&
      (!filters.dateMax || ev.date <= filters.dateMax)
    );
  });

  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div>
      <h1>Événements</h1>

      {/* Filtres */}
      <div className="filters">
        <input placeholder="Titre" onChange={e => setFilters({ ...filters, title: e.target.value })} />
        <input placeholder="Lieu" onChange={e => setFilters({ ...filters, location: e.target.value })} />
        <input type="date" onChange={e => setFilters({ ...filters, dateMin: e.target.value })} />
        <input type="date" onChange={e => setFilters({ ...filters, dateMax: e.target.value })} />
      </div>

      {/* Liste paginée */}
      <div className="card-list">
        {paginated.map(ev => (
          <EventCard key={ev.id} event={ev} />
        ))}
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>Précédent</button>
        <span>Page {page}</span>
        <button disabled={page * pageSize >= filtered.length} onClick={() => setPage(page + 1)}>Suivant</button>
      </div>
    </div>
  );
}