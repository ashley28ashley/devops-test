import {
  mockStats,
  mockEvents,
  mockCategories,
  mockCities,
  mockSearch,
  getMockEventDetail,
  type Stats,
  type EventList,
  type EventDetail,
  type CategoryBase,
  type CityBase,
  type SearchResult,
} from "./mock-data"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""

async function apiFetch<T>(path: string, fallback: () => T): Promise<T> {
  if (!API_BASE) return fallback()

  try {
    const res = await fetch(`${API_BASE}${path}`)
    if (!res.ok) throw new Error(`API error: ${res.status}`)
    return await res.json()
  } catch {
    return fallback()
  }
}

// --- API functions ---

export async function fetchStats(): Promise<Stats> {
  return apiFetch("/stats", () => mockStats)
}

export interface EventFilters {
  page?: number
  page_size?: number
  category?: string
  arrondissement?: string
  is_free?: boolean
  is_weekend?: boolean
  season?: string
}

export async function fetchEvents(filters: EventFilters = {}): Promise<EventList> {
  const params = new URLSearchParams()
  if (filters.page) params.set("page", String(filters.page))
  if (filters.page_size) params.set("page_size", String(filters.page_size))
  if (filters.category) params.set("category", filters.category)
  if (filters.arrondissement) params.set("arrondissement", filters.arrondissement)
  if (filters.is_free !== undefined) params.set("is_free", String(filters.is_free))
  if (filters.is_weekend !== undefined) params.set("is_weekend", String(filters.is_weekend))
  if (filters.season) params.set("season", filters.season)

  const query = params.toString() ? `?${params.toString()}` : ""

  return apiFetch(`/events${query}`, () => {
    let filtered = [...mockEvents]

    if (filters.category) {
      filtered = filtered.filter((e) => e.category_name === filters.category)
    }
    if (filters.arrondissement) {
      filtered = filtered.filter((e) => e.arrondissement === filters.arrondissement)
    }
    if (filters.is_free !== undefined) {
      filtered = filtered.filter((e) => e.is_free === filters.is_free)
    }

    const page = filters.page || 1
    const pageSize = filters.page_size || 20
    const start = (page - 1) * pageSize
    const end = start + pageSize

    return {
      total: filtered.length,
      page,
      page_size: pageSize,
      total_pages: Math.ceil(filtered.length / pageSize),
      events: filtered.slice(start, end),
    }
  })
}

export async function fetchEvent(id: number): Promise<EventDetail | null> {
  return apiFetch(`/events/${id}`, () => getMockEventDetail(id))
}

export async function fetchCategories(): Promise<CategoryBase[]> {
  return apiFetch("/categories", () => mockCategories)
}

export async function fetchCities(): Promise<CityBase[]> {
  return apiFetch("/cities", () => mockCities)
}

export async function searchEvents(query: string): Promise<SearchResult[]> {
  if (!query || query.length < 2) return []
  return apiFetch(`/search?q=${encodeURIComponent(query)}&limit=20`, () => mockSearch(query))
}
