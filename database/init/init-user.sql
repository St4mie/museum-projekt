-- database/init/init-users.sql

-- ---------------------------------------------------------
-- Legt alle gewünschten DB-Accounts an und vergibt Rechte.
-- Wird nur beim allerersten Start ausgeführt.
-- ---------------------------------------------------------

-- 1) Test-Datenbank (wenn noch nicht existiert) anlegen
CREATE DATABASE IF NOT EXISTS `museum_db_test`
  /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

-- 2) In die Haupt-Datenbank wechseln
USE `museum_db`;

-- 3) Entwickler (volle Rechte für Migrationen)
CREATE USER IF NOT EXISTS 'entwickler'@'%' IDENTIFIED BY '${DB_MIGRATE_PASSWORD}';
GRANT ALL PRIVILEGES ON `museum_db`.* TO 'entwickler'@'%';
GRANT ALL PRIVILEGES ON `museum_db_test`.* TO 'entwickler'@'%';

-- 4) Museum (CRUD für Content-Management)
CREATE USER IF NOT EXISTS 'museum'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT SELECT, INSERT, UPDATE, DELETE ON `museum_db`.* TO 'museum'@'%';

-- 5) Service (Import- und API-User)
CREATE USER IF NOT EXISTS 'service'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT 
    SELECT, INSERT,    -- Lese- und Schreib-Daten
    CREATE, ALTER       -- Tabellen anlegen / ändern
  ON `museum_db`.* TO 'service'@'%';

-- 6) Rechte für Test-Datenbank an Service geben
GRANT 
    SELECT, INSERT, 
    CREATE, ALTER, DROP
  ON `museum_db_test`.* TO 'service'@'%';

-- 7) Test-User (dedizierter User für Integrationstests)
CREATE USER IF NOT EXISTS 'test_user'@'%' IDENTIFIED BY '${TEST_DATABASE_PASSWORD}';
GRANT ALL PRIVILEGES ON `museum_db_test`.* TO 'test_user'@'%';

-- 8) System (Read-Only, Monitoring)
CREATE USER IF NOT EXISTS 'system'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT SELECT ON `museum_db`.* TO 'system'@'%';

-- 9) Benutzer (öffentliche Leserechte)
CREATE USER IF NOT EXISTS 'benutzer'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT SELECT ON `museum_db`.* TO 'benutzer'@'%';

FLUSH PRIVILEGES;
