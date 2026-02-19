-- ============================================================
-- SCHÉMA SQL - BASE CULTURAL EVENTS
-- PostgreSQL 15+
-- ============================================================

-- Suppression des tables existantes (ordre important pour les FK)
DROP TABLE IF EXISTS event_categories CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

-- ============================================================
-- TABLE: cities
-- Informations sur les villes
-- ============================================================
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    postcode VARCHAR(10),
    event_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: categories
-- Catégories d'événements
-- ============================================================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    parent_category VARCHAR(100),
    description TEXT,
    event_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: events
-- Événements culturels enrichis
-- ============================================================
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    
    -- Identification
    raw_id VARCHAR(24) UNIQUE NOT NULL,  -- ObjectId MongoDB
    source VARCHAR(50) NOT NULL,
    
    -- Informations principales
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Localisation
    city_id INTEGER REFERENCES cities(id),
    address_street VARCHAR(255),
    address_name VARCHAR(255),
    zipcode VARCHAR(10),
    arrondissement VARCHAR(10),
    
    -- Géolocalisation
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    distance_center DECIMAL(6, 2),  -- km du centre
    geocoded BOOLEAN DEFAULT FALSE,
    
    -- Dates et temps
    event_date DATE,
    event_datetime TIMESTAMP,
    event_end_date DATE,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,  -- 1=Lundi, 7=Dimanche
    day_of_week_name VARCHAR(20),
    month_name VARCHAR(20),
    season VARCHAR(20),
    time_period VARCHAR(20),  -- Matin, Après-midi, Soir, Nuit
    is_weekend BOOLEAN DEFAULT FALSE,
    is_multi_day BOOLEAN DEFAULT FALSE,
    duration_days INTEGER,
    
    -- Prix et accessibilité
    price_type VARCHAR(50),
    price_detail VARCHAR(255),
    is_free BOOLEAN DEFAULT FALSE,
    accessibility_score DECIMAL(3, 2),  -- 0.00 à 1.00
    
    -- Contact
    contact_url VARCHAR(500),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: event_categories
-- Relation Many-to-Many entre events et categories
-- ============================================================
CREATE TABLE event_categories (
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,  -- Catégorie principale
    confidence DECIMAL(3, 2),  -- Score de confiance 0.00-1.00
    PRIMARY KEY (event_id, category_id)
);

-- ============================================================
-- INDEX POUR PERFORMANCES
-- ============================================================

-- Index sur les dates (requêtes fréquentes)
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_datetime ON events(event_datetime);
CREATE INDEX idx_events_year_month ON events(year, month);
CREATE INDEX idx_events_season ON events(season);
CREATE INDEX idx_events_weekend ON events(is_weekend);

-- Index géospatiaux
CREATE INDEX idx_events_location ON events(latitude, longitude);
CREATE INDEX idx_events_arrondissement ON events(arrondissement);
CREATE INDEX idx_events_zipcode ON events(zipcode);
CREATE INDEX idx_events_city_id ON events(city_id);

-- Index pour recherche
CREATE INDEX idx_events_title ON events USING gin(to_tsvector('french', title));
CREATE INDEX idx_events_description ON events USING gin(to_tsvector('french', description));

-- Index sur les filtres courants
CREATE INDEX idx_events_is_free ON events(is_free);
CREATE INDEX idx_events_source ON events(source);
CREATE INDEX idx_events_day_of_week ON events(day_of_week);

-- Index sur la relation categories
CREATE INDEX idx_event_categories_event ON event_categories(event_id);
CREATE INDEX idx_event_categories_category ON event_categories(category_id);
CREATE INDEX idx_event_categories_primary ON event_categories(is_primary);

-- ============================================================
-- VUES UTILES
-- ============================================================

-- Vue : Événements avec leurs catégories principales
CREATE OR REPLACE VIEW events_with_categories AS
SELECT 
    e.*,
    c.name AS category_name,
    c.parent_category,
    ec.confidence
FROM events e
LEFT JOIN event_categories ec ON e.id = ec.event_id AND ec.is_primary = TRUE
LEFT JOIN categories c ON ec.category_id = c.id;

-- Vue : Statistiques par arrondissement
CREATE OR REPLACE VIEW stats_by_arrondissement AS
SELECT 
    arrondissement,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE is_free = TRUE) AS free_events,
    COUNT(*) FILTER (WHERE is_weekend = TRUE) AS weekend_events,
    ROUND(AVG(accessibility_score), 2) AS avg_accessibility,
    ROUND(AVG(distance_center), 2) AS avg_distance_center
FROM events
WHERE arrondissement IS NOT NULL
GROUP BY arrondissement
ORDER BY total_events DESC;

-- Vue : Statistiques par catégorie
CREATE OR REPLACE VIEW stats_by_category AS
SELECT 
    c.name AS category,
    c.parent_category,
    COUNT(DISTINCT e.id) AS total_events,
    COUNT(*) FILTER (WHERE e.is_free = TRUE) AS free_events,
    ROUND(AVG(e.accessibility_score), 2) AS avg_accessibility
FROM categories c
LEFT JOIN event_categories ec ON c.id = ec.category_id
LEFT JOIN events e ON ec.event_id = e.id
GROUP BY c.id, c.name, c.parent_category
ORDER BY total_events DESC;

-- Vue : Calendrier des événements
CREATE OR REPLACE VIEW events_calendar AS
SELECT 
    event_date,
    day_of_week_name,
    season,
    COUNT(*) AS total_events,
    COUNT(*) FILTER (WHERE is_free = TRUE) AS free_events,
    STRING_AGG(DISTINCT arrondissement, ', ' ORDER BY arrondissement) AS arrondissements
FROM events
GROUP BY event_date, day_of_week_name, season
ORDER BY event_date;

-- ============================================================
-- FONCTIONS UTILES
-- ============================================================

-- Fonction : Recherche plein texte
CREATE OR REPLACE FUNCTION search_events(search_query TEXT)
RETURNS TABLE (
    id INTEGER,
    title VARCHAR(500),
    description TEXT,
    event_date DATE,
    category_name VARCHAR(100),
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.title,
        e.description,
        e.event_date,
        c.name AS category_name,
        ts_rank(
            to_tsvector('french', e.title || ' ' || COALESCE(e.description, '')),
            plainto_tsquery('french', search_query)
        ) AS rank
    FROM events e
    LEFT JOIN event_categories ec ON e.id = ec.event_id AND ec.is_primary = TRUE
    LEFT JOIN categories c ON ec.category_id = c.id
    WHERE to_tsvector('french', e.title || ' ' || COALESCE(e.description, '')) 
          @@ plainto_tsquery('french', search_query)
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TRIGGER : Mise à jour automatique de updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DONNÉES INITIALES
-- ============================================================

-- Insertion des catégories principales
INSERT INTO categories (name, parent_category, description) VALUES
    ('Musique', NULL, 'Concerts et événements musicaux'),
    ('Jazz', 'Musique', 'Concerts de jazz'),
    ('Classique', 'Musique', 'Musique classique et orchestres'),
    ('Rock', 'Musique', 'Concerts rock, metal, punk'),
    ('Pop', 'Musique', 'Musique pop et variété'),
    ('Electro', 'Musique', 'Musique électronique'),
    ('Rap/Hip-Hop', 'Musique', 'Rap et hip-hop'),
    ('Chanson française', 'Musique', 'Chanson et variété française'),
    ('World', 'Musique', 'Musiques du monde'),
    
    ('Théâtre', NULL, 'Spectacles de théâtre'),
    ('Comédie', 'Théâtre', 'Pièces comiques'),
    ('Drame', 'Théâtre', 'Pièces dramatiques'),
    ('Contemporain', 'Théâtre', 'Théâtre contemporain'),
    
    ('Danse', NULL, 'Spectacles de danse'),
    ('Ballet', 'Danse', 'Ballet classique'),
    ('Hip-Hop', 'Danse', 'Danse hip-hop'),
    
    ('Exposition', NULL, 'Expositions et musées'),
    ('Art contemporain', 'Exposition', 'Art contemporain'),
    ('Peinture', 'Exposition', 'Expositions de peinture'),
    ('Sculpture', 'Exposition', 'Expositions de sculpture'),
    ('Photographie', 'Exposition', 'Expositions photo'),
    ('Art classique', 'Exposition', 'Art classique'),
    
    ('Cinéma', NULL, 'Projections et festivals'),
    ('Avant-première', 'Cinéma', 'Avant-premières'),
    ('Festival', 'Cinéma', 'Festivals de cinéma'),
    
    ('Conférence', NULL, 'Conférences et débats'),
    ('Sport', NULL, 'Événements sportifs'),
    ('Autre', NULL, 'Autres événements')
ON CONFLICT (name) DO NOTHING;

-- Insertion de Paris comme ville principale
INSERT INTO cities (name, department, postcode) VALUES
    ('Paris', 'Paris', '75000')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- COMMENTAIRES SUR LES TABLES
-- ============================================================
COMMENT ON TABLE events IS 'Événements culturels enrichis';
COMMENT ON TABLE categories IS 'Catégories et sous-catégories d''événements';
COMMENT ON TABLE cities IS 'Villes et métadonnées';
COMMENT ON TABLE event_categories IS 'Relation Many-to-Many events-categories';

COMMENT ON COLUMN events.raw_id IS 'Référence ObjectId MongoDB (events_raw)';
COMMENT ON COLUMN events.accessibility_score IS 'Score d''accessibilité 0-1 (gratuit, proche, géocodé, weekend)';
COMMENT ON COLUMN events.distance_center IS 'Distance en km du centre de Paris (Notre-Dame)';

-- ============================================================
-- FIN DU SCHÉMA
-- ============================================================

-- Afficher les tables créées
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;