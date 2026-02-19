import { useEffect, useState } from "react";
import { getEvents } from "../services/api";
import StatsCard from "../components/StatsCard";

export default function Dashboard() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    getEvents().then(setEvents);
  }, []);

  const total = events.length;

  const byLocation = events.reduce((acc, ev) => {
    acc[ev.location] = (acc[ev.location] || 0) + 1;
    return acc;
  }, {});

  const nextEvent = [...events].sort((a, b) => a.date.localeCompare(b.date))[0];

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <StatsCard title="Total événements" value={total} />
        <StatsCard title="Prochain événement" value={nextEvent?.title || "Aucun"} />
        <StatsCard title="Lieux différents" value={Object.keys(byLocation).length} />
      </div>
    </div>
  );
}