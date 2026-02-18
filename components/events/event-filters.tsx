"use client"

import { useCallback } from "react"
import { Filter, X } from "lucide-react"

interface EventFiltersProps {
  category: string
  arrondissement: string
  freeOnly: boolean
  onCategoryChange: (v: string) => void
  onArrondissementChange: (v: string) => void
  onFreeOnlyChange: (v: boolean) => void
  categories: string[]
}

const arrondissements = [
  "1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e", "9e", "10e",
  "11e", "12e", "13e", "14e", "15e", "16e", "17e", "18e", "19e", "20e",
]

export function EventFilters({
  category,
  arrondissement,
  freeOnly,
  onCategoryChange,
  onArrondissementChange,
  onFreeOnlyChange,
  categories,
}: EventFiltersProps) {
  const hasFilters = category || arrondissement || freeOnly

  const clearAll = useCallback(() => {
    onCategoryChange("")
    onArrondissementChange("")
    onFreeOnlyChange(false)
  }, [onCategoryChange, onArrondissementChange, onFreeOnlyChange])

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-sm font-medium text-card-foreground">
          <Filter className="h-4 w-4" />
          <span>Filtres</span>
        </div>

        {/* Category select */}
        <select
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Toutes categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        {/* Arrondissement select */}
        <select
          value={arrondissement}
          onChange={(e) => onArrondissementChange(e.target.value)}
          className="rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Tous arrondissements</option>
          {arrondissements.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>

        {/* Free toggle */}
        <button
          onClick={() => onFreeOnlyChange(!freeOnly)}
          className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
            freeOnly
              ? "border-primary bg-primary/15 text-primary"
              : "border-border bg-input text-muted-foreground hover:text-foreground"
          }`}
        >
          Gratuit uniquement
        </button>

        {/* Clear filters */}
        {hasFilters && (
          <button
            onClick={clearAll}
            className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
            Effacer
          </button>
        )}
      </div>
    </div>
  )
}
