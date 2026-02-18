import { CalendarDays, Tag, MapPin, Gift, Sun } from "lucide-react"
import type { Stats } from "@/lib/mock-data"

interface StatsCardsProps {
  stats: Stats
}

const cards = [
  { key: "total_events" as const, label: "Total evenements", icon: CalendarDays },
  { key: "total_categories" as const, label: "Categories", icon: Tag },
  { key: "total_cities" as const, label: "Villes", icon: MapPin },
  { key: "free_events" as const, label: "Evenements gratuits", icon: Gift },
  { key: "weekend_events" as const, label: "Weekend", icon: Sun },
]

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      {cards.map((card) => (
        <div
          key={card.key}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <card.icon className="h-4 w-4 text-primary" />
            </div>
            <p className="text-xs font-medium text-muted-foreground">{card.label}</p>
          </div>
          <p className="mt-3 text-2xl font-bold text-card-foreground">
            {stats[card.key].toLocaleString("fr-FR")}
          </p>
        </div>
      ))}
    </div>
  )
}
