import random
import sqlite3

DB_PATH = "demo.db"

COMPANIES = [
    ("Berliner Logistik GmbH", "Logistik", "Sabine Krause"),
    ("Müller & Partner AG", "Steuerberatung", "Thomas Müller"),
    ("TechSolutions Süd GmbH", "IT-Dienstleistung", "Aylin Demir"),
    ("Hanseatische Versicherung", "Versicherung", "Jens Petersen"),
    ("Grünfeld Energie e.K.", "Erneuerbare Energien", "Clara Grünfeld"),
    ("Nordlicht Consulting", "Beratung", "Marek Nowak"),
    ("Alpenblick Tourismus AG", "Tourismus", "Luisa Hofer"),
    ("Kaiser Fahrzeugtechnik GmbH", "Maschinenbau", "Dieter Kaiser"),
    ("Rhein-Main Digital GmbH", "Software", "Nadine Schmitt"),
    ("Lumen Pharma AG", "Pharma", "Dr. Elias Brand"),
]

EVENTS = [
    ("Workshop Führung im Wandel", "Workshop", "2025-03-12", "München", 40),
    ("Workshop Effektive Teamkommunikation", "Workshop", "2025-03-26", "Berlin", 30),
    ("Workshop Agile Methoden kompakt", "Workshop", "2025-04-09", "Hamburg", 45),
    ("Workshop Zeitmanagement & Fokus", "Workshop", "2025-04-23", "Frankfurt", 25),
    ("Workshop Design Thinking Basics", "Workshop", "2025-05-07", "Stuttgart", 50),
    ("Seminar Konfliktmanagement", "Seminar", "2025-05-21", "Köln", 35),
    ("Seminar Verhandlungstraining", "Seminar", "2025-06-04", "Düsseldorf", 40),
    ("Online-Workshop KI-Tools im Arbeitsalltag", "Online-Workshop", "2025-06-18", "Online", 20),
    ("Keynote Zukunft der Arbeit", "Keynote", "2025-07-02", "Berlin", 15),
    ("Teamevent Outdoor-Tag", "Teamevent", "2025-07-16", "Chiemsee", 30),
    ("Workshop Gesunde Führung", "Workshop", "2025-08-13", "Hamburg", 35),
    ("Workshop Präsentationstraining", "Workshop", "2025-09-10", "Leipzig", 30),
    ("Seminar Projektmanagement Basis", "Seminar", "2025-09-24", "Nürnberg", 45),
    ("Workshop Excel für Profis", "Workshop", "2025-10-08", "Online", 25),
    ("Teamevent Koch Workshop", "Teamevent", "2025-10-22", "Berlin", 35),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS bookings;
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS companies;
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT NOT NULL,
            contact TEXT NOT NULL,
            points_contingent INTEGER NOT NULL DEFAULT 200
        );
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            point_cost INTEGER NOT NULL,
            host_company_id INTEGER NOT NULL REFERENCES companies(id)
        );
        CREATE TABLE bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL REFERENCES companies(id),
            event_id INTEGER NOT NULL REFERENCES events(id),
            participants INTEGER NOT NULL,
            booked_at TEXT NOT NULL
        );
        """
    )

    cur.executemany(
        "INSERT INTO companies (name, industry, contact, points_contingent) VALUES (?, ?, ?, 200)",
        COMPANIES,
    )

    random.seed(42)
    n = len(COMPANIES)
    for idx, (title, etype, date, location, cost) in enumerate(EVENTS):
        host_id = idx % n + 1
        cur.execute(
            "INSERT INTO events (title, type, date, location, point_cost, host_company_id) VALUES (?, ?, ?, ?, ?, ?)",
            (title, etype, date, location, cost, host_id),
        )
        event_id = cur.lastrowid
        month = int(date[5:7])
        cur.execute(
            "INSERT INTO bookings (company_id, event_id, participants, booked_at) VALUES (?, ?, ?, ?)",
            (host_id, event_id, random.randint(8, 25), date),
        )
        other_ids = [c + 1 for c in range(n) if c + 1 != host_id]
        guests = random.sample(other_ids, random.randint(1, 4))
        for guest_id in guests:
            cur.execute(
                "INSERT INTO bookings (company_id, event_id, participants, booked_at) VALUES (?, ?, ?, ?)",
                (guest_id, event_id, random.randint(2, 10), date),
            )

    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    conn.close()
    print(f"Datenbank '{DB_PATH}' erzeugt: {len(COMPANIES)} Unternehmen, {len(EVENTS)} Events, {total} Buchungen (Hosts + Gäste).")


if __name__ == "__main__":
    seed()
