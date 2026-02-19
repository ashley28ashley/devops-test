import { NavLink } from "react-router-dom";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h2 className="logo">CulturalEvents</h2>

      <nav>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/events">Événements</NavLink>
        <NavLink to="/stats">Statistiques</NavLink>
      </nav>
    </aside>
  );
}