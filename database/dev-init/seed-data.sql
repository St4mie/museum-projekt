-- Fügt Beispiel-Filme für die Entwicklungsumgebung hinzu

USE museum_db;

INSERT INTO movie (title, release_year, director, author, main_cast, poster_url, description)
VALUES
  (
    'Inception',
    2010,
    'Christopher Nolan',
    'Christopher Nolan',
    'Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page',
    'https://example.com/inception.jpg',
    'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.'
  ),
  (
    'The Matrix',
    1999,
    'Lana Wachowski, Lilly Wachowski',
    'Lana Wachowski, Lilly Wachowski',
    'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss',
    'https://example.com/matrix.jpg',
    'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.'
  );
