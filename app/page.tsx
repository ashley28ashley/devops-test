import { fetchStats } from "@/lib/api"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { CategoryChart } from "@/components/dashboard/category-chart"
import { ArrondissementChart } from "@/components/dashboard/arrondissement-chart"
import { SeasonChart } from "@/components/dashboard/season-chart"

export default async function DashboardPage() {
  const stats = await fetchStats()

  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Vue d{"'"}ensemble des evenements culturels parisiens
        </p>
      </div>

      {/* KPI Cards */}
      <StatsCards stats={stats} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CategoryChart data={stats.by_category} />
        <ArrondissementChart data={stats.by_arrondissement} />
      </div>

      {/* Season Chart */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SeasonChart data={stats.by_season} />
        <div className="rounded-xl border border-border bg-card p-5 lg:col-span-2">
          <h3 className="mb-4 text-sm font-semibold text-card-foreground">
            A propos du projet
          </h3>
          <div className="flex flex-col gap-3 text-sm text-muted-foreground leading-relaxed">
            <p>
              Ce dashboard visualise les donnees issues du pipeline DevOps complet pour les
              evenements culturels parisiens.
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-lg bg-secondary/50 p-3">
                <p className="mb-1 text-xs font-semibold text-primary">Collecte</p>
                <p className="text-xs">API Open Data Paris vers MongoDB</p>
              </div>
              <div className="rounded-lg bg-secondary/50 p-3">
                <p className="mb-1 text-xs font-semibold text-primary">ETL</p>
                <p className="text-xs">Transformation et chargement PostgreSQL</p>
              </div>
              <div className="rounded-lg bg-secondary/50 p-3">
                <p className="mb-1 text-xs font-semibold text-accent">Enrichissement</p>
                <p className="text-xs">Geocodage, categorisation, analyse temporelle</p>
              </div>
              <div className="rounded-lg bg-secondary/50 p-3">
                <p className="mb-1 text-xs font-semibold text-accent">API REST</p>
                <p className="text-xs">FastAPI avec filtres, recherche, statistiques</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
