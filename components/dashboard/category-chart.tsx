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

interface CategoryChartProps {
  data: Stats["by_category"]
}

export function CategoryChart({ data }: CategoryChartProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="mb-4 text-sm font-semibold text-card-foreground">
        Evenements par categorie
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 10, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.26 0.025 260)" />
            <XAxis type="number" tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 12 }} />
            <YAxis
              dataKey="name"
              type="category"
              width={100}
              tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 12 }}
            />
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
              fill="oklch(0.65 0.2 250)"
              radius={[0, 4, 4, 0]}
              maxBarSize={24}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
