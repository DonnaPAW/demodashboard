import sqlite3
from collections import defaultdict

DB_PATH = "demo.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_companies():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM companies ORDER BY name").fetchall()


def company_report(company_id):
    with get_connection() as conn:
        company = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
        if company is None:
            return None

        booked = conn.execute(
            """
            SELECT e.*, b.participants, b.booked_at
            FROM bookings b
            JOIN events e ON e.id = b.event_id
            WHERE b.company_id = ?
            ORDER BY e.date
            """,
            (company_id,),
        ).fetchall()

        booked_ids = [row["id"] for row in booked]
        guests = defaultdict(list)
        if booked_ids:
            placeholders = ",".join("?" * len(booked_ids))
            rows = conn.execute(
                f"""
                SELECT b.event_id, c.name
                FROM bookings b
                JOIN companies c ON c.id = b.company_id
                WHERE b.event_id IN ({placeholders})
                """,
                booked_ids,
            ).fetchall()
            for row in rows:
                if row["name"] != company["name"]:
                    guests[row["event_id"]].append(row["name"])

        events_with_guests = [
            dict(row, guests=sorted(guests[row["id"]])) for row in booked
        ]

        other_events = conn.execute(
            """
            SELECT e.*, b.participants, c.name AS host_name
            FROM bookings b
            JOIN events e ON e.id = b.event_id
            JOIN companies c ON c.id = e.host_company_id
            WHERE b.company_id = ? AND e.host_company_id != ?
            ORDER BY e.date
            """,
            (company_id, company_id),
        ).fetchall()

        points_used = sum(e["point_cost"] for e in booked)
        workshop_count = sum(1 for e in booked if e["type"] == "Workshop")
        hosted_count = conn.execute(
            "SELECT COUNT(*) FROM events WHERE host_company_id = ?",
            (company_id,),
        ).fetchone()[0]

        return {
            "company": company,
            "events": events_with_guests,
            "other_events": other_events,
            "points_used": points_used,
            "points_left": company["points_contingent"] - points_used,
            "workshop_count": workshop_count,
            "event_count": len(booked),
            "hosted_count": hosted_count,
        }


def overview():
    with get_connection() as conn:
        companies = conn.execute("SELECT * FROM companies ORDER BY name").fetchall()
        totals = conn.execute(
            "SELECT COUNT(*) AS events, SUM(point_cost) AS cost FROM events"
        ).fetchone()
        bookings_count = conn.execute("SELECT COUNT(*) AS n FROM bookings").fetchone()["n"]

        rows = conn.execute(
            """
            SELECT c.id, c.name, c.industry, c.contact, c.points_contingent,
                   COALESCE(SUM(e.point_cost), 0) AS points_used,
                   COUNT(b.id) AS bookings,
                   SUM(CASE WHEN e.type = 'Workshop' THEN 1 ELSE 0 END) AS workshops
            FROM companies c
            LEFT JOIN bookings b ON b.company_id = c.id
            LEFT JOIN events e ON e.id = b.event_id
            GROUP BY c.id
            ORDER BY c.name
            """
        ).fetchall()

        return {
            "companies": rows,
            "total_events": totals["events"],
            "total_bookings": bookings_count,
        }
