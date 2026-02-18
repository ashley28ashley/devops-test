"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { Search, CalendarDays, Tag } from "lucide-react"
import { searchEvents } from "@/lib/api"
import type { SearchResult } from "@/lib/mock-data"

export default function SearchPage() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)

    if (query.length < 2) {
      setResults([])
      setSearched(false)
      return
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      const data = await searchEvents(query)
      setResults(data)
      setSearched(true)
      setLoading(false)
    }, 300)

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [query])

  return (
    <div className="mx-auto max-w-3xl">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">Recherche</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Recherchez parmi les evenements culturels
        </p>
      </div>

      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Rechercher un evenement, une categorie..."
          className="w-full rounded-xl border border-border bg-card py-3.5 pl-12 pr-4 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-ring"
          autoFocus
        />
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      )}

      {/* Results */}
      {!loading && searched && (
        <div className="mt-6">
          <p className="mb-4 text-sm text-muted-foreground">
            {results.length} resultat{results.length !== 1 ? "s" : ""} pour &quot;{query}&quot;
          </p>

          {results.length === 0 ? (
            <div className="rounded-xl border border-border bg-card p-8 text-center">
              <p className="text-sm text-muted-foreground">
                Aucun evenement ne correspond a votre recherche.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {results.map((result) => (
                <Link
                  key={result.id}
                  href={`/events/${result.id}`}
                  className="rounded-xl border border-border bg-card p-4 transition-colors hover:bg-secondary/30"
                >
                  <h3 className="text-sm font-medium text-card-foreground">
                    {result.title}
                  </h3>
                  {result.description && (
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                      {result.description}
                    </p>
                  )}
                  <div className="mt-2 flex flex-wrap items-center gap-3">
                    {result.category_name && (
                      <span className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Tag className="h-3 w-3" />
                        {result.category_name}
                      </span>
                    )}
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <CalendarDays className="h-3 w-3" />
                      {new Date(result.event_date).toLocaleDateString("fr-FR", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Initial state */}
      {!loading && !searched && (
        <div className="mt-12 text-center">
          <Search className="mx-auto h-12 w-12 text-muted-foreground/30" />
          <p className="mt-4 text-sm text-muted-foreground">
            Tapez au moins 2 caracteres pour lancer une recherche
          </p>
        </div>
      )}
    </div>
  )
}
