import "./StatsCard.css";

export default function StatsCard({ title, value }) {
  return (
    <div className="stats-card">
      <h4>{title}</h4>
      <p>{value}</p>
    </div>
  );
}