-- ######################################################################
-- # 01_seed_data.sql
-- #
-- # Befüllt die Tabelle „movie“ in der Datenbank „museum_db“ mit
-- # deutschen Film-Titeln (nur title + release_year). Alle weiteren
-- # Spalten (description, director, etc.) bleiben auf ihrem Standard-Wert,
-- # sodass ihr per Wiki-Import (POST /movies/import/{id}) echte Metadaten
-- # nachziehen könnt.
-- ######################################################################

-- 1) Stelle sicher, dass wir in der richtigen Datenbank arbeiten:
USE `museum_db`;

-- 2) Einfügen von deutschen Filmen
--    Die Tabelle „movie“ sollte bereits per Migration existieren.

INSERT INTO movie (titel, erscheinungsjahr) VALUES
    ('Metropolis',                     1927),
    ('M – Eine Stadt sucht einen Mörder',1931),
    ('Der blaue Engel',                1930),
    ('Nosferatu – Eine Symphonie des Grauens', 1922),
    ('Das Cabinet des Dr. Caligari',   1920),
    ('Die Brücke',                     1959),
    ('Das Boot',                       1981),
    ('Fitzcarraldo',                   1982),
    ('Die Ehe der Maria Braun',        1979),
    ('Aguirre, der Zorn Gottes',       1972),
    ('Lola rennt',                     1998),
    ('Good Bye, Lenin!',               2003),
    ('Das Leben der Anderen',          2006),
    ('Der Untergang',                  2004),
    ('Die Fälscher',                   2007),
    ('Das weiße Band',                 2009),
    ('Oh Boy',                         2012),
    ('Victoria',                       2015),
    ('Toni Erdmann',                   2016),
    ('Werk ohne Autor',                2018),
    ('Berlin Alexanderplatz',          1980),
    ('Heimat',                         1984);

-- Hinweise:
-- - Nur title und release_year werden hier befüllt, alle anderen Spalten bleiben NULL bzw. FALSE.
