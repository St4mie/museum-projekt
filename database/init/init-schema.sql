-- ######################################################################
-- # database/init/init-schema.sql
-- #
-- # Grundschema für die Datenbank `museum_db` mit allen empfohlenen
-- # Einstellungen, Indizes und Kommentaren.
-- ######################################################################

-- 1) Datenbank anlegen (wenn sie noch nicht existiert), inkl. Zeichensatz
CREATE DATABASE IF NOT EXISTS `museum_db`
  /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `museum_db`;

-- 2) Tabelle `movie` anlegen (falls noch nicht vorhanden)
--    Wir nutzen InnoDB für Transaktionen und stellen sicher,
--    dass TEXT-Spalten einen definierten Zeichensatz erben.
CREATE TABLE IF NOT EXISTS `movie` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,

  `title` VARCHAR(255) NOT NULL COMMENT 'Filmtitel',
  `wiki_url` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'Link zum Wikipedia-Eintrag',
  `release_year` SMALLINT UNSIGNED COMMENT 'Erscheinungsjahr',
  `director` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'Regisseur',
  `author` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'Drehbuchautor',
  `main_cast` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'Hauptdarsteller (kommagetrennt)',
  `poster_url` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'URL zum Filmplakat',
  `description` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    COMMENT 'Kurzbeschreibung / Plot',

  `review` BOOLEAN NOT NULL DEFAULT FALSE
    COMMENT 'Markierung bei Import-Fehlern',

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    COMMENT 'Zeitpunkt der Erstellung',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
    COMMENT 'Zeitpunkt der letzten Änderung',

  -- 3) Indizes für performantere Suche
  INDEX (`title`),
  INDEX (`release_year`),

  -- 4) Fulltext-Index auf Texte für bessere Volltext-Suchen
  FULLTEXT INDEX `ft_title_description` (`title`, `description`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Filme (Import aus Wikipedia)';

-- 5) Optional: if you later add lookup-tables (e.g. genres), you could
--    define foreign keys here.

