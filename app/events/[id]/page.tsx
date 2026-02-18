import Link from "next/link"
import { fetchEvent } from "@/lib/api"
import {
  ArrowLeft,
  CalendarDays,
  MapPin,
  Clock,
  Globe,
  Phone,
  Mail,
  Tag,
  Euro,
  Sun,
  Compass,
} from "lucide-react"

interface PageProps {
  params: Promise<{ id: string }>
}

export default async function EventDetailPage({ params }: PageProps) {
  const { id } = await params
  const event = await fetchEvent(Number(id))

  if (!event) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-lg font-medium text-foreground">Evenement introuvable</p>
        <Link
          href="/events"
          className="mt-4 flex items-center gap-2 text-sm text-primary hover:underline"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour aux evenements
        </Link>
      </div>
    )
  }

  const dateFormatted = new Date(event.event_date).toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  })

  return (
    <div className="mx-auto max-w-4xl">
      {/* Back link */}
      <Link
        href="/events"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Retour aux evenements
      </Link>

      {/* Header */}
      <div className="rounded-xl border border-border bg-card p-6">
        <div className="flex flex-wrap items-start gap-3">
          {event.category_name && (
            <span className="inline-block rounded-md bg-primary/15 px-2.5 py-1 text-xs font-semibold text-primary">
              {event.category_name}
            </span>
          )}
          <span
            className={`inline-block rounded-md px-2.5 py-1 text-xs font-semibold ${
              event.is_free
                ? "bg-accent/15 text-accent"
                : "bg-secondary text-secondary-foreground"
            }`}
          >
            {event.is_free ? "Gratuit" : "Payant"}
          </span>
          {event.is_weekend && (
            <span className="inline-block rounded-md bg-chart-3/15 px-2.5 py-1 text-xs font-semibold text-chart-3">
              Weekend
            </span>
          )}
        </div>
        <h1 className="mt-4 text-2xl font-bold text-balance text-card-foreground">
          {event.title}
        </h1>
        {event.description && (
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
            {event.description}
          </p>
        )}
      </div>

      {/* Details grid */}
      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Date and time */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="mb-4 text-sm font-semibold text-card-foreground">Date et horaires</h2>
          <div className="flex flex-col gap-3">
            <DetailRow icon={CalendarDays} label="Date" value={dateFormatted} />
            {event.day_of_week_name && (
              <DetailRow icon={Clock} label="Jour" value={event.day_of_week_name} />
            )}
            {event.time_period && (
              <DetailRow icon={Clock} label="Periode" value={event.time_period} />
            )}
            {event.season && (
              <DetailRow icon={Sun} label="Saison" value={event.season} />
            )}
            {event.is_multi_day && event.duration_days && (
              <DetailRow icon={CalendarDays} label="Duree" value={`${event.duration_days} jours`} />
            )}
          </div>
        </div>

        {/* Location */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="mb-4 text-sm font-semibold text-card-foreground">Localisation</h2>
          <div className="flex flex-col gap-3">
            {event.city_name && (
              <DetailRow icon={MapPin} label="Ville" value={event.city_name} />
            )}
            {event.arrondissement && (
              <DetailRow icon={Compass} label="Arrondissement" value={event.arrondissement} />
            )}
            {event.address_street && (
              <DetailRow icon={MapPin} label="Adresse" value={event.address_street} />
            )}
            {event.zipcode && (
              <DetailRow icon={MapPin} label="Code postal" value={event.zipcode} />
            )}
            {event.distance_center !== null && (
              <DetailRow
                icon={Compass}
                label="Distance centre"
                value={`${event.distance_center} km`}
              />
            )}
          </div>
        </div>

        {/* Pricing */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="mb-4 text-sm font-semibold text-card-foreground">Tarification</h2>
          <div className="flex flex-col gap-3">
            {event.price_type && (
              <DetailRow icon={Euro} label="Type" value={event.price_type} />
            )}
            {event.price_detail && (
              <DetailRow icon={Tag} label="Detail" value={event.price_detail} />
            )}
            {event.accessibility_score !== null && (
              <DetailRow
                icon={Tag}
                label="Accessibilite"
                value={`${Math.round(event.accessibility_score * 100)}%`}
              />
            )}
          </div>
        </div>

        {/* Contact */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="mb-4 text-sm font-semibold text-card-foreground">Contact</h2>
          <div className="flex flex-col gap-3">
            {event.contact_url && (
              <div className="flex items-start gap-3">
                <Globe className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">Site web</p>
                  <a
                    href={event.contact_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    {event.contact_url}
                  </a>
                </div>
              </div>
            )}
            {event.contact_phone && (
              <DetailRow icon={Phone} label="Telephone" value={event.contact_phone} />
            )}
            {event.contact_email && (
              <DetailRow icon={Mail} label="Email" value={event.contact_email} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function DetailRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm text-card-foreground">{value}</p>
      </div>
    </div>
  )
}
