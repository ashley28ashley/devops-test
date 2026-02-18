"use client"

import { useState, useEffect, useCallback } from "react"
import { fetchEvents, fetchCategories } from "@/lib/api"
import type { EventList, CategoryBase } from "@/lib/mock-data"
import { EventFilters } from "@/components/events/event-filters"
import { EventTable } from "@/components/events/event-table"

export default function EventsPage() {
  const [data, setData] = useState<EventList | null>(null)
  const [categories, setCategories] = useState<CategoryBase[]>([])
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState("")
  const [arrondissement, setArrondissement] = useState("")
  const [freeOnly, setFreeOnly] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadEvents = useCallback(async () => {
    setLoading(true)
    const result = await fetchEvents({
      page,
      page_size: 20,
      category: category || undefined,
      arrondissement: arrondissement || undefined,
      is_free: freeOnly ? true : undefined,
    })
    setData(result)
    setLoading(false)
  }, [page, category, arrondissement, freeOnly])

  useEffect(() => {
    loadEvents()
  }, [loadEvents])

  useEffect(() => {
    fetchCategories().then(setCategories)
  }, [])

  // Reset page on filter change
  const handleCategoryChange = useCallback((v: string) => {
    setCategory(v)
    setPage(1)
  }, [])

  const handleArrondissementChange = useCallback((v: string) => {
    setArrondissement(v)
    setPage(1)
  }, [])

  const handleFreeOnlyChange = useCallback((v: boolean) => {
    setFreeOnly(v)
    setPage(1)
  }, [])

  const parentCategories = categories
    .filter((c) => c.parent_category === null)
    .map((c) => c.name)

  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Evenements</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Parcourir et filtrer les evenements culturels
        </p>
      </div>

      {/* Filters */}
      <EventFilters
        category={category}
        arrondissement={arrondissement}
        freeOnly={freeOnly}
        onCategoryChange={handleCategoryChange}
        onArrondissementChange={handleArrondissementChange}
        onFreeOnlyChange={handleFreeOnlyChange}
        categories={parentCategories}
      />

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : data ? (
        <EventTable
          events={data.events}
          total={data.total}
          page={data.page}
          totalPages={data.total_pages}
          onPageChange={setPage}
        />
      ) : (
        <p className="py-10 text-center text-muted-foreground">
          Aucun evenement trouve.
        </p>
      )}
    </div>
  )
}
