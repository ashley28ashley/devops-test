import { useEffect, useState } from "react";
import { getStats } from "../services/api";

export default function StatsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      console.error("Erreur chargement stats:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 rounded-full border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!stats) {
    return <p className="text-center mt-10">Impossible de charger les statistiques.</p>;
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      <h1 className="text-3xl font-bold mb-8">Statistiques globales</h1>

      {/* --- CARDS --- */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-12">
        <StatCard label="Total événements" value={stats.total_events} />
        <StatCard label="Événements gratuits" value={stats.free_events} />
        <StatCard label="Événements weekend" value={stats.weekend_events} />
        <StatCard label="Catégories uniques" value={stats.total_categories} />
        <StatCard label="Villes couvertes" value={stats.total_cities} />
      </div>

      {/* --- CATÉGORIES --- */}
      <Section
        title="Répartition par catégorie"
        data={stats.by_category}
        field="name"
      />

      {/* --- SAISONS --- */}
      <Section
        title="Répartition par saison"
        data={stats.by_season}
        field="season"
      />

      {/* --- ARRONDISSEMENTS --- */}
      <Section
        title="Répartition par arrondissement"
        data={stats.by_arrondissement}
        field="arrondissement"
      />

    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white shadow rounded-lg p-6 text-center">
      <div className="text-gray-500 text-sm">{label}</div>
      <div className="text-2xl font-bold mt-2">{value}</div>
    </div>
  );
}

function Section({ title, data, field }) {
  return (
    <div className="mb-10">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="bg-white shadow rounded-lg p-6">
        {data.length === 0 && <p className="text-gray-500">Aucune donnée</p>}

        {data.map((item, i) => (
          <div key={i} className="flex justify-between py-1 border-b last:border-none">
            <span>{item[field]}</span>
            <span className="font-semibold">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}