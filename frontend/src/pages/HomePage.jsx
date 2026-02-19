import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Calendar, MapPin } from 'lucide-react';
import { getEvents, getCategories, searchEvents } from '../services/api';

export default function HomePage() {
  const [eventsData, setEventsData] = useState({
    total: 0,
    page: 1,
    total_pages: 1,
    events: []
  });

  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 20,
    is_free: null,
    is_weekend: null,
    category: null,
    arrondissement: null
  });

  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    loadEvents();
    loadCategories();
  }, [filters]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await getEvents(filters);

      // data = { total, page, page_size, total_pages, events }
      setEventsData(data);
    } catch (error) {
      console.error('Erreur chargement événements:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error('Erreur chargement catégories:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const results = await searchEvents(searchQuery);

      setEventsData({
        total: results.length,
        page: 1,
        total_pages: 1,
        events: results
      });
    } catch (error) {
      console.error('Erreur recherche:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* Barre de recherche */}
      <div className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Rechercher un événement..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Search className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Filtres */}
      <div className="mb-6 flex flex-wrap gap-4">

        {/* Gratuit */}
        <button
          onClick={() => setFilters({ ...filters, is_free: filters.is_free ? null : true })}
          className={`px-4 py-2 rounded-lg border ${
            filters.is_free ? 'bg-primary-600 text-white' : 'bg-white hover:bg-gray-50'
          }`}
        >
          Gratuit
        </button>

        {/* Weekend */}
        <button
          onClick={() => setFilters({ ...filters, is_weekend: filters.is_weekend ? null : true })}
          className={`px-4 py-2 rounded-lg border ${
            filters.is_weekend ? 'bg-primary-600 text-white' : 'bg-white hover:bg-gray-50'
          }`}
        >
          Weekend
        </button>

        {/* Catégories */}
<select
  value={filters.category || ''}
  onChange={(e) => setFilters({...filters, category: e.target.value || null, page: 1})}
  className="px-4 py-2 border rounded-lg"
>
  <option value="">Toutes catégories</option>
  {categories
    .filter(c => !c.parent_category)  
    .map(cat => (
      <option key={cat.id} value={cat.name}>{cat.name}</option>
    ))}
</select>

        {/* Arrondissements */}
        <select
          value={filters.arrondissement || ''}
          onChange={(e) => setFilters({ ...filters, arrondissement: e.target.value || null })}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="">Tous arrondissements</option>
          {Array.from({ length: 20 }, (_, i) => i + 1).map(n => (
            <option key={n} value={`${n}${n === 1 ? 'er' : 'e'}`}>
              {n}{n === 1 ? 'er' : 'e'}
            </option>
          ))}
        </select>
      </div>

      {/* Résultats */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement...</p>
        </div>
      ) : (
        <>
          <div className="mb-4 text-sm text-gray-600">
            {eventsData.total} événement(s) trouvé(s)
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {eventsData.events.map((event) => (
              <div
                key={event.id}
                onClick={() => navigate(`/events/${event.id}`)}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer p-6"
              >
                <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                  {event.title}
                </h3>

                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2" />
                    {event.event_date
                      ? new Date(event.event_date).toLocaleDateString('fr-FR')
                      : "Date non renseignée"}
                  </div>

                  {event.arrondissement && (
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-2" />
                      {event.arrondissement} arrondissement
                    </div>
                  )}

                  {event.is_free && (
                    <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                      Gratuit
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {eventsData.total_pages > 1 && (
            <div className="mt-8 flex justify-center gap-2">
              <button
                disabled={filters.page === 1}
                onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Précédent
              </button>

              <span className="px-4 py-2">
                Page {filters.page} / {eventsData.total_pages}
              </span>

              <button
                disabled={filters.page >= eventsData.total_pages}
                onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Suivant
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}