"use client"

import Link from "next/link"
import { CalendarDays, MapPin, ChevronLeft, ChevronRight } from "lucide-react"
import type { EventBase } from "@/lib/mock-data"

interface EventTableProps {
  events: EventBase[]
  total: number
  page: number
  totalPages: number
  onPageChange: (page: number) => void
}

export function EventTable({ events, total, page, totalPages, onPageChange }: EventTableProps) {
  return (
    <div className="rounded-xl border border-border bg-card">
      {/* Table header info */}
      <div className="flex items-center justify-between border-b border-border px-5 py-3">
        <p className="text-sm text-muted-foreground">
          {total.toLocaleString("fr-FR")} evenement{total > 1 ? "s" : ""} trouves
        </p>
        <p className="text-sm text-muted-foreground">
          Page {page} / {totalPages}
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Evenement
              </th>
              <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground sm:table-cell">
                Categorie
              </th>
              <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground md:table-cell">
                Arrondissement
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Date
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Prix
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {events.map((event) => (
              <tr
                key={event.id}
                className="transition-colors hover:bg-secondary/30"
              >
                <td className="px-5 py-3.5">
                  <Link
                    href={`/events/${event.id}`}
                    className="text-sm font-medium text-foreground hover:text-primary"
                  >
                    {event.title}
                  </Link>
                </td>
                <td className="hidden px-5 py-3.5 sm:table-cell">
                  {event.category_name && (
                    <span className="inline-block rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                      {event.category_name}
                    </span>
                  )}
                </td>
                <td className="hidden px-5 py-3.5 md:table-cell">
                  {event.arrondissement && (
                    <span className="flex items-center gap-1 text-sm text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      {event.arrondissement}
                    </span>
                  )}
                </td>
                <td className="px-5 py-3.5">
                  <span className="flex items-center gap-1 text-sm text-muted-foreground">
                    <CalendarDays className="h-3 w-3" />
                    {new Date(event.event_date).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    })}
                  </span>
                </td>
                <td className="px-5 py-3.5">
                  <span
                    className={`inline-block rounded-md px-2 py-0.5 text-xs font-medium ${
                      event.is_free
                        ? "bg-accent/15 text-accent"
                        : "bg-secondary text-secondary-foreground"
                    }`}
                  >
                    {event.is_free ? "Gratuit" : "Payant"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 border-t border-border px-5 py-3">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
            Precedent
          </button>
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              let pageNum: number
              if (totalPages <= 5) {
                pageNum = i + 1
              } else if (page <= 3) {
                pageNum = i + 1
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i
              } else {
                pageNum = page - 2 + i
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => onPageChange(pageNum)}
                  className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm font-medium transition-colors ${
                    pageNum === page
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
          </div>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:opacity-40"
          >
            Suivant
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}
