"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts"
import type { Stats } from "@/lib/mock-data"

interface ArrondissementChartProps {
  data: Stats["by_arrondissement"]
}

export function ArrondissementChart({ data }: ArrondissementChartProps) {
  const sortedData = [...data].sort((a, b) => b.count - a.count).slice(0, 12)

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="mb-4 text-sm font-semibold text-card-foreground">
        Top arrondissements
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sortedData} margin={{ bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.26 0.025 260)" vertical={false} />
            <XAxis
              dataKey="arrondissement"
              tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={50}
            />
            <YAxis tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.17 0.02 260)",
                border: "1px solid oklch(0.26 0.025 260)",
                borderRadius: "0.5rem",
                color: "oklch(0.95 0.01 260)",
                fontSize: 13,
              }}
              formatter={(value: number) => [value.toLocaleString("fr-FR"), "Evenements"]}
            />
            <Bar
              dataKey="count"
              fill="oklch(0.55 0.18 160)"
              radius={[4, 4, 0, 0]}
              maxBarSize={32}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
