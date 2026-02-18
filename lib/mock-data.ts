// Mock data matching the FastAPI response models for standalone demo

export interface EventBase {
  id: number
  title: string
  event_date: string
  arrondissement: string | null
  is_free: boolean
  category_name?: string | null
}

export interface EventDetail extends EventBase {
  description: string | null
  city_name: string | null
  address_street: string | null
  address_name: string | null
  zipcode: string | null
  latitude: number | null
  longitude: number | null
  distance_center: number | null
  event_datetime: string | null
  year: number | null
  month: number | null
  month_name: string | null
  day_of_week_name: string | null
  season: string | null
  time_period: string | null
  is_weekend: boolean
  is_multi_day: boolean
  duration_days: number | null
  price_type: string | null
  price_detail: string | null
  accessibility_score: number | null
  contact_url: string | null
  contact_phone: string | null
  contact_email: string | null
  parent_category: string | null
}

export interface EventList {
  total: number
  page: number
  page_size: number
  total_pages: number
  events: EventBase[]
}

export interface CategoryBase {
  id: number
  name: string
  parent_category: string | null
}

export interface CityBase {
  id: number
  name: string
  event_count: number
}

export interface Stats {
  total_events: number
  total_categories: number
  total_cities: number
  free_events: number
  weekend_events: number
  by_category: { name: string; count: number }[]
  by_arrondissement: { arrondissement: string; count: number }[]
  by_season: { season: string; count: number }[]
}

export interface SearchResult {
  id: number
  title: string
  description: string | null
  event_date: string
  category_name: string | null
  rank: number
}

// --- Mock Stats ---
export const mockStats: Stats = {
  total_events: 1247,
  total_categories: 28,
  total_cities: 1,
  free_events: 523,
  weekend_events: 412,
  by_category: [
    { name: "Exposition", count: 287 },
    { name: "Musique", count: 234 },
    { name: "Theatre", count: 189 },
    { name: "Conference", count: 145 },
    { name: "Danse", count: 112 },
    { name: "Cinema", count: 98 },
    { name: "Art contemporain", count: 67 },
    { name: "Jazz", count: 52 },
    { name: "Classique", count: 38 },
    { name: "Sport", count: 25 },
  ],
  by_arrondissement: [
    { arrondissement: "4e", count: 178 },
    { arrondissement: "1er", count: 156 },
    { arrondissement: "6e", count: 134 },
    { arrondissement: "3e", count: 121 },
    { arrondissement: "5e", count: 112 },
    { arrondissement: "11e", count: 98 },
    { arrondissement: "7e", count: 87 },
    { arrondissement: "10e", count: 76 },
    { arrondissement: "18e", count: 65 },
    { arrondissement: "13e", count: 54 },
    { arrondissement: "14e", count: 48 },
    { arrondissement: "9e", count: 42 },
    { arrondissement: "8e", count: 38 },
    { arrondissement: "15e", count: 34 },
    { arrondissement: "2e", count: 28 },
    { arrondissement: "16e", count: 24 },
    { arrondissement: "19e", count: 22 },
    { arrondissement: "20e", count: 18 },
    { arrondissement: "12e", count: 14 },
    { arrondissement: "17e", count: 10 },
  ],
  by_season: [
    { season: "Automne", count: 387 },
    { season: "Printemps", count: 342 },
    { season: "Ete", count: 298 },
    { season: "Hiver", count: 220 },
  ],
}

// --- Mock Events ---
const eventTitles = [
  "Exposition Monet - Lumieres impressionnistes",
  "Concert Jazz au Sunset",
  "Festival du Theatre d'Avignon a Paris",
  "Conference sur l'Intelligence Artificielle",
  "Ballet du Lac des Cygnes - Opera de Paris",
  "Nuit Blanche 2025 - Art contemporain",
  "Retrospective Picasso au Grand Palais",
  "Orchestre de Paris - Symphonie n.9",
  "Festival du Cinema Independant",
  "Atelier Danse Hip-Hop pour tous",
  "Exposition Photographie - Regards Croises",
  "Concert Rock indie au Bataclan",
  "Theatre - Le Malade Imaginaire",
  "Conference Climat et Biodiversite",
  "Danse Contemporaine - Cie Preljocaj",
  "Vernissage Galerie Perrotin",
  "Concert Chanson Francaise",
  "Opera - Carmen de Bizet",
  "Festival Electro - Nuit Parisienne",
  "Exposition Sculpture au Jardin des Tuileries",
  "Theatre - Cyrano de Bergerac",
  "Concert Classique a la Sainte-Chapelle",
  "Atelier Peinture - Les Couleurs de Paris",
  "Festival Rap Francais - Zenith",
  "Exposition Manga au Musee du Quai Branly",
  "Conference Philosophie - Existentialisme",
  "Spectacle de Magie Moderne",
  "Concert World Music - Africa Fete",
  "Theatre - En attendant Godot",
  "Cinema en Plein Air - La Villette",
]

const categories = [
  "Exposition", "Musique", "Theatre", "Conference", "Danse",
  "Cinema", "Art contemporain", "Jazz", "Classique", "Sport",
  "Rock", "Pop", "Electro", "Rap/Hip-Hop", "Chanson francaise",
]

const arrondissements = [
  "1er", "2e", "3e", "4e", "5e", "6e", "7e", "8e", "9e", "10e",
  "11e", "12e", "13e", "14e", "15e", "16e", "17e", "18e", "19e", "20e",
]

const seasons = ["Printemps", "Ete", "Automne", "Hiver"]
const dayNames = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
const monthNames = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"]

function generateEvents(count: number): EventBase[] {
  const events: EventBase[] = []
  for (let i = 1; i <= count; i++) {
    const month = Math.floor(Math.random() * 12)
    const day = Math.floor(Math.random() * 28) + 1
    events.push({
      id: i,
      title: eventTitles[(i - 1) % eventTitles.length],
      event_date: `2025-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`,
      arrondissement: arrondissements[Math.floor(Math.random() * arrondissements.length)],
      is_free: Math.random() > 0.58,
      category_name: categories[Math.floor(Math.random() * categories.length)],
    })
  }
  return events.sort((a, b) => a.event_date.localeCompare(b.event_date))
}

export const mockEvents: EventBase[] = generateEvents(120)

export function getMockEventDetail(id: number): EventDetail | null {
  const base = mockEvents.find((e) => e.id === id)
  if (!base) return null

  const dateObj = new Date(base.event_date)
  const dayOfWeek = dateObj.getDay()
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
  const month = dateObj.getMonth()
  const season = month >= 2 && month <= 4 ? "Printemps" : month >= 5 && month <= 7 ? "Ete" : month >= 8 && month <= 10 ? "Automne" : "Hiver"

  return {
    ...base,
    description: `Decouvrez cet evenement exceptionnel a Paris. ${base.title} est un moment incontournable de la scene culturelle parisienne. Venez nombreux profiter de cette experience unique dans le ${base.arrondissement || "centre"} de Paris.`,
    city_name: "Paris",
    address_street: `${Math.floor(Math.random() * 200) + 1} Rue de Rivoli`,
    address_name: "Centre Culturel",
    zipcode: `750${String(Math.floor(Math.random() * 20) + 1).padStart(2, "0")}`,
    latitude: 48.8566 + (Math.random() - 0.5) * 0.05,
    longitude: 2.3522 + (Math.random() - 0.5) * 0.08,
    distance_center: Math.round(Math.random() * 8 * 100) / 100,
    event_datetime: `${base.event_date}T${String(Math.floor(Math.random() * 12) + 10).padStart(2, "0")}:00:00`,
    year: dateObj.getFullYear(),
    month: month + 1,
    month_name: monthNames[month],
    day_of_week_name: dayNames[dayOfWeek === 0 ? 6 : dayOfWeek - 1],
    season,
    time_period: Math.random() > 0.5 ? "Soir" : "Apres-midi",
    is_weekend: isWeekend,
    is_multi_day: Math.random() > 0.7,
    duration_days: Math.random() > 0.7 ? Math.floor(Math.random() * 5) + 2 : 1,
    price_type: base.is_free ? "Gratuit" : "Payant",
    price_detail: base.is_free ? "Entree libre" : `${Math.floor(Math.random() * 35) + 5} EUR`,
    accessibility_score: Math.round(Math.random() * 100) / 100,
    contact_url: "https://www.paris.fr/evenements",
    contact_phone: "+33 1 42 76 40 40",
    contact_email: "contact@paris-culture.fr",
    parent_category: null,
  }
}

// --- Mock Categories ---
export const mockCategories: CategoryBase[] = [
  { id: 1, name: "Musique", parent_category: null },
  { id: 2, name: "Jazz", parent_category: "Musique" },
  { id: 3, name: "Classique", parent_category: "Musique" },
  { id: 4, name: "Rock", parent_category: "Musique" },
  { id: 5, name: "Pop", parent_category: "Musique" },
  { id: 6, name: "Electro", parent_category: "Musique" },
  { id: 7, name: "Rap/Hip-Hop", parent_category: "Musique" },
  { id: 8, name: "Chanson francaise", parent_category: "Musique" },
  { id: 9, name: "World", parent_category: "Musique" },
  { id: 10, name: "Theatre", parent_category: null },
  { id: 11, name: "Comedie", parent_category: "Theatre" },
  { id: 12, name: "Drame", parent_category: "Theatre" },
  { id: 13, name: "Contemporain", parent_category: "Theatre" },
  { id: 14, name: "Danse", parent_category: null },
  { id: 15, name: "Ballet", parent_category: "Danse" },
  { id: 16, name: "Hip-Hop", parent_category: "Danse" },
  { id: 17, name: "Exposition", parent_category: null },
  { id: 18, name: "Art contemporain", parent_category: "Exposition" },
  { id: 19, name: "Peinture", parent_category: "Exposition" },
  { id: 20, name: "Photographie", parent_category: "Exposition" },
  { id: 21, name: "Cinema", parent_category: null },
  { id: 22, name: "Conference", parent_category: null },
  { id: 23, name: "Sport", parent_category: null },
  { id: 24, name: "Autre", parent_category: null },
]

// --- Mock Cities ---
export const mockCities: CityBase[] = [
  { id: 1, name: "Paris", event_count: 1247 },
]

// --- Mock Search ---
export function mockSearch(query: string): SearchResult[] {
  const q = query.toLowerCase()
  return mockEvents
    .filter(
      (e) =>
        e.title.toLowerCase().includes(q) ||
        (e.category_name && e.category_name.toLowerCase().includes(q))
    )
    .slice(0, 20)
    .map((e, i) => ({
      id: e.id,
      title: e.title,
      description: `Evenement culturel a Paris - ${e.category_name || "Divers"}`,
      event_date: e.event_date,
      category_name: e.category_name || null,
      rank: 1 - i * 0.05,
    }))
}
