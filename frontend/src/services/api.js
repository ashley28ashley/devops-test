const API_URL = "http://localhost:8000";

/**
 * Construit une query string propre (ignore null / undefined / "")
 */
function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== null &&
      value !== undefined &&
      value !== "" &&
      value !== "null"
    ) {
      searchParams.append(key, value);
    }
  });

  return searchParams.toString();
}

/**
 * Récupère les événements avec filtres
 */
export async function getEvents(params = {}) {
  const queryString = buildQueryString(params);
  const url = queryString
    ? `${API_URL}/events?${queryString}`
    : `${API_URL}/events`;

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error("Erreur lors de la récupération des événements");
  }

  return res.json();
}

/**
 * Récupère un événement par son ID
 */
export async function getEvent(id) {
  const res = await fetch(`${API_URL}/events/${id}`);

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("Événement non trouvé");
    }
    throw new Error("Erreur lors de la récupération de l'événement");
  }

  return res.json();
}

/**
 * Recherche d'événements
 */
export async function searchEvents(query, limit = 20) {
  const queryString = buildQueryString({ q: query, limit });
  const res = await fetch(`${API_URL}/search?${queryString}`);

  if (!res.ok) {
    throw new Error("Erreur lors de la recherche");
  }

  return res.json();
}

/**
 * Récupère les catégories
 */
export async function getCategories() {
  const res = await fetch(`${API_URL}/categories`);

  if (!res.ok) {
    throw new Error("Erreur lors de la récupération des catégories");
  }

  return res.json();
}

/**
 * Récupère les villes
 */
export async function getCities() {
  const res = await fetch(`${API_URL}/cities`);

  if (!res.ok) {
    throw new Error("Erreur lors de la récupération des villes");
  }

  return res.json();
}

/**
 * Récupère les statistiques
 */
export async function getStats() {
  const res = await fetch(`${API_URL}/stats`);

  if (!res.ok) {
    throw new Error("Erreur lors de la récupération des statistiques");
  }

  return res.json();
}

/**
 * Health check
 */
export async function getHealth() {
  const res = await fetch(`${API_URL}/health`);

  if (!res.ok) {
    throw new Error("API non disponible");
  }

  return res.json();
}

// Export par défaut pour compatibilité
const api = {
  getEvents,
  getEvent,
  searchEvents,
  getCategories,
  getCities,
  getStats,
  healthCheck: getHealth,
};

export default api;
