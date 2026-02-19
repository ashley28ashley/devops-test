import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Calendar, MapPin, Tag, DollarSign, ArrowLeft, ExternalLink } from 'lucide-react';
import { getEvent } from "../services/api";

export default function EventDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvent();
  }, [id]);

  const loadEvent = async () => {
    try {
      const data = await getEvent(id);
      setEvent(data);
    } catch (error) {
      console.error('Erreur chargement événement:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-gray-600">Événement non trouvé</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 text-primary-600 hover:text-primary-700"
          >
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/')}
        className="mb-6 flex items-center text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour
      </button>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6">{event.title}</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          
          {/* Date */}
          {event.event_date && (
            <div className="flex items-start">
              <Calendar className="h-5 w-5 mr-3 mt-1 text-gray-400" />
              <div>
                <div className="font-medium">Date</div>
                <div className="text-gray-600">
                  {new Date(event.event_date).toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </div>
                {event.day_of_week_name && (
                  <div className="text-sm text-gray-500">{event.day_of_week_name}</div>
                )}
                {event.time_period && (
                  <div className="text-sm text-gray-500">{event.time_period}</div>
                )}
              </div>
            </div>
          )}

          {/* Lieu */}
          <div className="flex items-start">
            <MapPin className="h-5 w-5 mr-3 mt-1 text-gray-400" />
            <div>
              <div className="font-medium">Lieu</div>
              {event.address_name && <div className="text-gray-600">{event.address_name}</div>}
              {event.address_street && <div className="text-gray-600">{event.address_street}</div>}
              <div className="text-gray-600">
                {event.zipcode} {event.city_name || 'Paris'}
              </div>
              {event.arrondissement && (
                <div className="text-sm text-gray-500">{event.arrondissement} arrondissement</div>
              )}
            </div>
          </div>

          {/* Catégorie */}
          {event.category_name && (
            <div className="flex items-start">
              <Tag className="h-5 w-5 mr-3 mt-1 text-gray-400" />
              <div>
                <div className="font-medium">Catégorie</div>
                <div className="text-gray-600">{event.category_name}</div>
                {event.parent_category && (
                  <div className="text-sm text-gray-500">{event.parent_category}</div>
                )}
              </div>
            </div>
          )}

          {/* Prix */}
          <div className="flex items-start">
            <DollarSign className="h-5 w-5 mr-3 mt-1 text-gray-400" />
            <div>
              <div className="font-medium">Tarif</div>
              {event.is_free ? (
                <span className="inline-block px-3 py-1 bg-green-100 text-green-800 text-sm rounded">
                  Gratuit
                </span>
              ) : (
                <div className="text-gray-600">
                  {event.price_detail || event.price_type || 'Payant'}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        {event.description && (
          <div className="mb-6 border-t pt-6">
            <h2 className="text-xl font-semibold mb-3">Description</h2>
            <div
              className="text-gray-700 prose max-w-none"
              dangerouslySetInnerHTML={{ __html: event.description }}
            />
          </div>
        )}

        {/* Infos additionnelles */}
        {(event.season || event.is_weekend || event.accessibility_score) && (
          <div className="border-t pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {event.season && (
                <div>
                  <div className="text-gray-500">Saison</div>
                  <div className="font-medium">{event.season}</div>
                </div>
              )}
              
              {event.is_weekend && (
                <div>
                  <div className="text-gray-500">Weekend</div>
                  <div className="font-medium text-orange-600">Oui</div>
                </div>
              )}
              
              {event.accessibility_score && (
                <div>
                  <div className="text-gray-500">Accessibilité</div>
                  <div className="font-medium">{(event.accessibility_score * 100).toFixed(0)}%</div>
                </div>
              )}

              {event.distance_center && (
                <div>
                  <div className="text-gray-500">Distance centre</div>
                  <div className="font-medium">{event.distance_center.toFixed(1)} km</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Contact */}
        {event.contact_url && (
          <div className="mt-6 pt-6 border-t">
            <a
              href={event.contact_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Plus d'informations
              <ExternalLink className="h-4 w-4 ml-2" />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}