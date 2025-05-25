-- Grundschema für die Datenbank museum_db
CREATE DATABASE IF NOT EXISTS museum_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE museum_db;

-- Tabelle für Film-Entitäten (Import aus Wikipedia)
CREATE TABLE IF NOT EXISTS movie (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(255) NOT NULL,   -- Filmtitel
  wiki_url      TEXT,                    -- Link zum Wikipedia-Eintrag
  release_year  INT,                     -- Erscheinungsjahr
  director      VARCHAR(255),            -- Regisseur
  author        VARCHAR(255),            -- Drehbuchautor
  main_cast     TEXT,                    -- Hauptdarsteller (kommagetrennt)
  poster_url    TEXT,                    -- URL zum Filmplakat
  description   TEXT,                    -- Kurzbeschreibung / Plot
  review        BOOLEAN NOT NULL DEFAULT FALSE,  -- Markierung bei Import-Fehlern
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                  ON UPDATE CURRENT_TIMESTAMP
);
