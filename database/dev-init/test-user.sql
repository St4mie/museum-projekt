-- Legt einen Entwickler-Test-User an, für automatisierte Integrationstests

USE museum_db;

CREATE USER IF NOT EXISTS 'tests'@'%' IDENTIFIED BY 'Test123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON museum_db.* TO 'test'@'%';
FLUSH PRIVILEGES;
