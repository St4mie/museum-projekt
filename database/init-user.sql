-- database/init/init-users.sql
-- ---------------------------------------------------------
-- Legt alle gewünschten DB-Accounts an und vergibt Rechte.
-- Wird nur beim allerersten Start ausgeführt.
-- ---------------------------------------------------------

USE museum_db;

-- Entwickler (volle Rechte für Migrationen)
CREATE USER IF NOT EXISTS 'entwickler'@'%' IDENTIFIED BY 'Starten2025!';
GRANT ALL PRIVILEGES ON museum_db.* TO 'entwickler'@'%';

-- Museum (CRUD für Content Management)
CREATE USER IF NOT EXISTS 'museum'@'%' IDENTIFIED BY 'Starten2025!';
GRANT SELECT, INSERT, UPDATE, DELETE ON museum_db.* TO 'museum'@'%';

-- Service (Import- und API-User, Lesen + Einfügen)
CREATE USER IF NOT EXISTS 'service'@'%' IDENTIFIED BY 'Starten2025!';
GRANT SELECT, INSERT ON museum_db.* TO 'service'@'%';

-- System (Read-Only, Monitoring)
CREATE USER IF NOT EXISTS 'system'@'%' IDENTIFIED BY 'Starten2025!';
GRANT SELECT ON museum_db.* TO 'system'@'%';

-- Benutzer (öffentliche Leserechte)
CREATE USER IF NOT EXISTS 'benutzer'@'%' IDENTIFIED BY 'Starten2025!';
GRANT SELECT ON museum_db.* TO 'benutzer'@'%';

FLUSH PRIVILEGES;
