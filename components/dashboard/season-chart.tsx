"use client"

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts"
import type { Stats } from "@/lib/mock-data"

interface SeasonChartProps {
  data: Stats["by_season"]
}

const SEASON_COLORS = [
  "oklch(0.65 0.2 250)",  // chart-1
  "oklch(0.55 0.18 160)", // chart-2
  "oklch(0.70 0.18 55)",  // chart-3
  "oklch(0.60 0.20 310)", // chart-4
]

export function SeasonChart({ data }: SeasonChartProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="mb-4 text-sm font-semibold text-card-foreground">
        Distribution saisonniere
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
              dataKey="count"
              nameKey="season"
              stroke="none"
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={SEASON_COLORS[index % SEASON_COLORS.length]} />
              ))}
            </Pie>
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
            <Legend
              formatter={(value) => (
                <span style={{ color: "oklch(0.65 0.02 260)", fontSize: 13 }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
