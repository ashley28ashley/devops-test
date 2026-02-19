import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Calendar, Map, BarChart3, Search } from 'lucide-react';
import HomePage from './pages/HomePage';
import MapPage from './pages/MapPage';
import StatsPage from './pages/StatsPage';
import EventDetailPage from './pages/EventDetailPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link 
                  to="/" 
                  className="inline-flex items-center px-1 pt-1 text-gray-900 font-medium"
                >
                  <Calendar className="h-5 w-5 mr-2" />
                  Événements Culturels Paris
                </Link>
              </div>
              
              <div className="flex space-x-4">
                <Link
                  to="/"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
                >
                  <Search className="h-4 w-4 mr-2" />
                  Explorer
                </Link>
                
                <Link
                  to="/map"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
                >
                  <Map className="h-4 w-4 mr-2" />
                  Carte
                </Link>
                
                <Link
                  to="/stats"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 rounded-md"
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Statistiques
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Contenu */}
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/map" element={<MapPage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/events/:id" element={<EventDetailPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t mt-12">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-500">
              Données : Paris Open Data • {new Date().getFullYear()}
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
