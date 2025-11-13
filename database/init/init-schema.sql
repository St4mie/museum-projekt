-- ######################################################################
-- Init-Schema für die Datenbank `museum_db`
-- Dieses Skript erweitert die bestehende Datenbank, ohne bereits vorhandene Strukturen zu verändern.
-- Es wurden alle Attributnamen in Deutsch gehalten, und Kommentare beschränken sich auf Funktion und Relationen.
-- ######################################################################

-- 1) Datenbank anlegen (falls nicht vorhanden) und Zeichensatz festlegen
CREATE DATABASE IF NOT EXISTS `museum_db`
  /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `museum_db`;

-- ######################################################################
-- 2) Tabelle movie (Bestehende Tabelle, unverändert)
--    Enthält grundlegende Filmdaten; keine Relationen zu anderen Tabellen.
-- ######################################################################
CREATE TABLE IF NOT EXISTS `movie` (
  `id`              INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `titel`           VARCHAR(255) NOT NULL,
  `wiki_url`        TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erscheinungsjahr` SMALLINT UNSIGNED,
  `regisseur`       VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `autor`           VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `hauptdarsteller` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `poster_url`      TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `beschreibung`    TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `pruefung`        BOOLEAN NOT NULL DEFAULT FALSE,
  `erstellt_am`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                     ON UPDATE CURRENT_TIMESTAMP,
  INDEX (`titel`),
  INDEX (`erscheinungsjahr`),
  FULLTEXT INDEX `ft_titel_beschreibung` (`titel`, `beschreibung`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Filme (Import aus Wikipedia)';

-- ######################################################################
-- 3) Neues Schema: Ausstellungen (werden neu angelegt, ohne bestehende Tabellen zu ändern)
-- ######################################################################

-- 3.1) Ausstellung
--     Eine Ausstellung kann mehrere Räume enthalten.
CREATE TABLE IF NOT EXISTS `ausstellung` (
  `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`          VARCHAR(255) NOT NULL,
  `beschreibung`  TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erstellt_am`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_ausstellung_name` (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Ausstellungen';

-- 3.2) Raum
--     Jeder Raum gehört genau zu einer Ausstellung.
CREATE TABLE IF NOT EXISTS `raum` (
  `id`               INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `ausstellung_id`   INT UNSIGNED NOT NULL,  -- FK → ausstellung.id
  `name`             VARCHAR(255) NOT NULL,
  `beschreibung`     TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erstellt_am`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                      ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`ausstellung_id`) REFERENCES `ausstellung`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_raum_ausstellung_name` (`ausstellung_id`, `name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Räume innerhalb einer Ausstellung';

-- 3.3) Regal
--     Ein Regal gehört zu genau einem Raum.
CREATE TABLE IF NOT EXISTS `regal` (
  `id`          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `raum_id`     INT UNSIGNED NOT NULL,  -- FK → raum.id
  `bezeichnung` VARCHAR(255) NOT NULL,
  `beschreibung` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erstellt_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`raum_id`) REFERENCES `raum`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_regal_raum_bezeichnung` (`raum_id`, `bezeichnung`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Regale in einem Raum';

-- 3.4) Fach
--     Ein Fach gehört zu genau einem Regal.
CREATE TABLE IF NOT EXISTS `fach` (
  `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `regal_id`     INT UNSIGNED NOT NULL,  -- FK → regal.id
  `bezeichnung`  VARCHAR(255) NOT NULL,
  `beschreibung` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erstellt_am`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                   ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`regal_id`) REFERENCES `regal`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_fach_regal_bezeichnung` (`regal_id`, `bezeichnung`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Fächer in einem Regal';

-- 3.5) Stellplatz
--     Ein Stellplatz gehört zu genau einem Fach.
CREATE TABLE IF NOT EXISTS `stellplatz` (
  `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `fach_id`       INT UNSIGNED NOT NULL,  -- FK → fach.id
  `position`      TINYINT UNSIGNED NOT NULL,
  `erstellt_am`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`fach_id`) REFERENCES `fach`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_stellplatz_fach_position` (`fach_id`, `position`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Stellplätze in einem Fach';

-- ######################################################################
-- 4) Neues Schema: Szenen, Medien und Exponate (bauen auf bestehender movie-Tabelle auf)
-- ######################################################################

-- 4.1) Szene
--     Eine Szene gehört zu genau einem Film (movie.id).
CREATE TABLE IF NOT EXISTS `szene` (
  `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `film_id`      INT UNSIGNED NOT NULL,  -- FK → movie.id
  `name`         VARCHAR(255) NOT NULL,
  `beschreibung` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `erstellt_am`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                  ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`film_id`) REFERENCES `movie`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_szene_film_name` (`film_id`, `name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Szenen zu Filmen';

-- 4.2) Medien (Audio/Video)
--     Jedes Medium gehört zu genau einer Szene.
CREATE TABLE IF NOT EXISTS `medium` (
  `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `szene_id`     INT UNSIGNED NOT NULL,        -- FK → szene.id
  `dateipfad`    VARCHAR(1024) NOT NULL,
  `medientyp`    ENUM('audio','video') NOT NULL,
  `erstellt_am`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                  ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`szene_id`) REFERENCES `szene`(`id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Audio- und Video-Medien pro Szene';

-- 4.3) Exponat
--     Ein Exponat kann in mehreren Szenen vorkommen (m:n-Beziehung).
CREATE TABLE IF NOT EXISTS `exponat` (
  `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`          VARCHAR(255) NOT NULL,
  `beschreibung`  TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `hersteller`    VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `baujahr`       SMALLINT UNSIGNED,
  `material`      VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `wert`          DECIMAL(12,2),
  `anzahl`        INT UNSIGNED DEFAULT 1,
  `erstellt_am`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `aktualisiert_am` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                   ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_exponat_name` (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Tabelle für Exponate';

-- 4.4) Zuordnung Szene ⇆ Exponat (m:n-Beziehung)
CREATE TABLE IF NOT EXISTS `szene_exponat` (
  `szene_id`     INT UNSIGNED NOT NULL,        -- FK → szene.id
  `exponat_id`   INT UNSIGNED NOT NULL,        -- FK → exponat.id
  PRIMARY KEY (`szene_id`, `exponat_id`),
  FOREIGN KEY (`szene_id`) REFERENCES `szene`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`exponat_id`) REFERENCES `exponat`(`id`) ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
  COMMENT = 'Junction-Tabelle für m:n-Beziehung zwischen Szenen und Exponaten';

-- 4.5) Zuordnung Stellplatz ⇆ Szene (1:1-Beziehung)
--     Ein Stellplatz kann genau eine Szene belegen; Fremdschlüssel ermöglicht SET NULL bei Löschung.
ALTER TABLE `stellplatz`
  ADD COLUMN `szene_id` INT UNSIGNED NULL,          -- FK → szene.id
  ADD UNIQUE KEY `uq_stellplatz_szene` (`szene_id`),
  ADD FOREIGN KEY (`szene_id`) REFERENCES `szene`(`id`) ON DELETE SET NULL;

-- ######################################################################
-- Prüfung: Diese Erweiterung fügt ausschließlich neue Tabellen und Spalten hinzu.
--           Die vorhandene `movie`-Tabelle bleibt unverändert.
-- ######################################################################
