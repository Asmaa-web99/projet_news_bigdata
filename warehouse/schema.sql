-- ============================================================
-- DATA WAREHOUSE : Star Schema pour analyse des news
-- ============================================================

DROP TABLE IF EXISTS fact_articles CASCADE;
DROP TABLE IF EXISTS dim_source CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_language CASCADE;

-- ===== DIMENSIONS =====

CREATE TABLE dim_source (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) UNIQUE NOT NULL,
    country VARCHAR(10),
    base_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_language (
    language_id SERIAL PRIMARY KEY,
    language_code VARCHAR(10) UNIQUE NOT NULL,
    language_name VARCHAR(50)
);

CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    date_value DATE UNIQUE NOT NULL,
    year INT,
    month INT,
    day INT,
    day_of_week VARCHAR(15),
    quarter INT
);

-- ===== FAIT =====

CREATE TABLE fact_articles (
    article_id VARCHAR(64) PRIMARY KEY,
    source_id INT REFERENCES dim_source(source_id),
    date_id INT REFERENCES dim_date(date_id),
    language_id INT REFERENCES dim_language(language_id),
    title TEXT,
    author VARCHAR(255),
    category VARCHAR(100),
    url TEXT,
    content TEXT,
    word_count INT,
    char_count INT,
    sentence_count INT,
    keywords_str TEXT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    positive_words_count INT,
    negative_words_count INT,
    publication_date VARCHAR(50),
    scraped_at TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== INDEX POUR PERFORMANCES =====

CREATE INDEX idx_fact_source ON fact_articles(source_id);
CREATE INDEX idx_fact_date ON fact_articles(date_id);
CREATE INDEX idx_fact_language ON fact_articles(language_id);
CREATE INDEX idx_fact_category ON fact_articles(category);

-- ===== DONNÉES INITIALES DES DIMENSIONS =====

INSERT INTO dim_language (language_code, language_name) VALUES
    ('fr', 'Français'),
    ('en', 'English'),
    ('ar', 'العربية'),
    ('unknown', 'Unknown')
ON CONFLICT DO NOTHING;

INSERT INTO dim_source (source_name, country, base_url) VALUES
    ('hespress', 'MA', 'https://fr.hespress.com'),
    ('akhbarona', 'MA', 'https://www.akhbarona.com'),
    ('bbc', 'UK', 'https://www.bbc.com/news'),
    ('aljazeera', 'QA', 'https://www.aljazeera.com'),
    ('franceinfo', 'FR', 'https://www.francetvinfo.fr')
ON CONFLICT DO NOTHING;