-- ######################################################################
-- # database/dev-init/test-user.sql
-- #
-- # Legt einen dedizierten Test-User an, der in CI/Integrationstests
-- # gegen die Dev-Datenbank verwendet wird.
-- ######################################################################

USE `museum_db`;

-- 1) Test-User anlegen (falls noch nicht vorhanden)
--    Wir verwenden einen eigenen User `tests`, um Tests sauber ablaufen
--    zu lassen und nicht die produktiven Nutzerkonten zu verwenden.
CREATE USER IF NOT EXISTS `tests`@`%`
  IDENTIFIED BY 'Test123!';

-- 2) Berechtigungen vergeben:
--    Dieser User soll in Tests das komplette Schema verändern dürfen,
--    daher SELECT, INSERT, UPDATE und DELETE auf alle Tabellen in museum_db.
GRANT
  SELECT,
  INSERT,
  UPDATE,
  DELETE
ON `museum_db`.* TO `tests`@`%`;

-- 3) Änderungen sofort wirksam machen
FLUSH PRIVILEGES;

-- ######################################################################
-- # Hinweise:
-- # - Das Passwort 'Test123!' sollte in CI/CD über Secrets injiziert werden.
-- # - Host '%' erlaubt Verbindungen von allen Adressen; im Dev-Umfeld ist
-- # - das in Ordnung, im Produktivbetrieb sollte man das einschränken.
-- ######################################################################
