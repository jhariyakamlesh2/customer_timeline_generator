"""Database and timeline services for Customer Timeline Generator.

This module contains the application's business logic and can be used
independently of the Streamlit user interface.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PROJECT_DIR / "crm_timeline.db"
CUSTOMERS_CSV = PROJECT_DIR / "data" / "customers.csv"
EVENTS_CSV = PROJECT_DIR / "data" / "customer_events.csv"

CUSTOMER_COLUMNS = [
    "customer_id", "customer_name", "email", "phone", "company", "segment", "joined_date"
]
EVENT_COLUMNS = [
    "event_id", "customer_id", "event_type", "event_date", "subject",
    "description", "status", "amount", "created_by"
]


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str | Path = DEFAULT_DB_PATH, seed: bool = True) -> None:
    """Create the database schema and load the bundled sample data once."""
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                segment TEXT,
                joined_date TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customer_events (
                event_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                event_type TEXT NOT NULL CHECK (event_type IN ('Call', 'Email', 'Ticket', 'Purchase')),
                event_date TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                created_by TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_events_customer_date
                ON customer_events(customer_id, event_date);
            CREATE INDEX IF NOT EXISTS idx_events_type
                ON customer_events(event_type);
            """
        )
        customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        event_count = conn.execute("SELECT COUNT(*) FROM customer_events").fetchone()[0]

        if seed and customer_count == 0:
            customers = pd.read_csv(CUSTOMERS_CSV, dtype={"customer_id": str})
            customers = customers[CUSTOMER_COLUMNS]
            customers.to_sql("customers", conn, if_exists="append", index=False)
        if seed and event_count == 0:
    events = pd.read_csv(
        EVENTS_CSV,
        dtype={"event_id": str, "customer_id": str}
    )

    events = events[EVENT_COLUMNS].copy()

    # Clean text columns
    for col in ["event_id", "customer_id", "status"]:
        events[col] = events[col].astype("string").str.strip()

    # Check required fields
    required_columns = ["event_id", "customer_id", "status"]

    for col in required_columns:
        invalid = (
            events[col].isna()
            | events[col].eq("")
            | events[col].str.lower().eq("nan")
        )

        if invalid.any():
            raise ValueError(
                f"Invalid or missing values in {col}. "
                f"Problematic rows: {events.index[invalid].tolist()}"
            )

    # Check duplicate event IDs
    if events["event_id"].duplicated().any():
        duplicates = events.loc[
            events["event_id"].duplicated(keep=False),
            "event_id"
        ].tolist()

        raise ValueError(f"Duplicate event IDs found: {duplicates}")

    # Convert amount to numeric
    events["amount"] = pd.to_numeric(
        events["amount"], errors="coerce"
    ).fillna(0.0)

    # Check that every event belongs to an existing customer
    customer_ids = pd.read_sql_query(
        "SELECT customer_id FROM customers",
        conn
    )["customer_id"].astype(str)

    missing_customers = ~events["customer_id"].isin(customer_ids)

    if missing_customers.any():
        raise ValueError(
            "Events reference customers that do not exist: "
            + str(events.loc[missing_customers, "customer_id"].tolist())
        )

    # Insert validated events
    events.to_sql(
        "customer_events",
        conn,
        if_exists="append",
        index=False
    )


def get_customers(db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Return all CRM customers ordered by name."""
    with get_connection(db_path) as conn:
        result = pd.read_sql_query(
            "SELECT customer_id, customer_name, email, phone, company, segment, joined_date "
            "FROM customers ORDER BY customer_name COLLATE NOCASE",
            conn,
        )
    return result


def get_customer_profile(customer_id: str, db_path: str | Path = DEFAULT_DB_PATH) -> Optional[dict]:
    """Return one customer's profile, or None when the ID does not exist."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT customer_id, customer_name, email, phone, company, segment, joined_date "
            "FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
    return dict(row) if row else None


def get_customer_events(
    customer_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    start_date: str | None = None,
    end_date: str | None = None,
    event_types: Iterable[str] | None = None,
    search_text: str | None = None,
) -> pd.DataFrame:
    """Fetch a customer's events, optionally filtered, in ascending date order.

    The ISO-style date format in SQLite (YYYY-MM-DD HH:MM) sorts chronologically.
    A secondary event_id sort makes events at the same time deterministic.
    """
    query = """
        SELECT event_id, customer_id, event_type, event_date, subject,
               description, status, amount, created_by
        FROM customer_events
        WHERE customer_id = ?
    """
    params: list[object] = [customer_id]

    if start_date:
        query += " AND date(event_date) >= date(?)"
        params.append(str(start_date))
    if end_date:
        query += " AND date(event_date) <= date(?)"
        params.append(str(end_date))

    selected_types = list(event_types) if event_types is not None else None
    if selected_types is not None:
        if not selected_types:
            # An explicitly empty selection means no event types were chosen.
            query += " AND 1 = 0"
        else:
            placeholders = ", ".join("?" for _ in selected_types)
            query += f" AND event_type IN ({placeholders})"
            params.extend(selected_types)

    if search_text and search_text.strip():
        query += " AND (subject LIKE ? OR description LIKE ? OR status LIKE ?)"
        wildcard = f"%{search_text.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    query += " ORDER BY datetime(event_date) ASC, event_id ASC"
    with get_connection(db_path) as conn:
        events = pd.read_sql_query(query, conn, params=params)

    if not events.empty:
        events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
        events["amount"] = pd.to_numeric(events["amount"], errors="coerce").fillna(0.0)
    else:
        events = pd.DataFrame(columns=EVENT_COLUMNS)
        events["event_date"] = pd.to_datetime(events["event_date"])
        events["amount"] = pd.to_numeric(events["amount"])
    return events


def generate_timeline(
    customer_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    **filters,
) -> list[dict]:
    """Generate the chronological timeline as a list of event dictionaries."""
    events = get_customer_events(customer_id, db_path=db_path, **filters)
    if events.empty:
        return []
    timeline = events.sort_values(["event_date", "event_id"], kind="stable")
    timeline = timeline.where(pd.notna(timeline), None)
    return timeline.to_dict(orient="records")


def get_customer_summary(customer_id: str, db_path: str | Path = DEFAULT_DB_PATH) -> dict:
    """Calculate headline activity metrics for a customer profile."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_events,
                SUM(CASE WHEN event_type = 'Call' THEN 1 ELSE 0 END) AS calls,
                SUM(CASE WHEN event_type = 'Email' THEN 1 ELSE 0 END) AS emails,
                SUM(CASE WHEN event_type = 'Ticket' THEN 1 ELSE 0 END) AS tickets,
                SUM(CASE WHEN event_type = 'Purchase' THEN 1 ELSE 0 END) AS purchases,
                SUM(CASE WHEN event_type = 'Ticket' AND status IN ('Open', 'Pending') THEN 1 ELSE 0 END) AS open_tickets,
                SUM(CASE WHEN event_type = 'Purchase' THEN amount ELSE 0 END) AS purchase_value
            FROM customer_events WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()
    return {key: (value if value is not None else 0) for key, value in dict(row).items()}


def add_event(
    customer_id: str,
    event_type: str,
    event_date: str,
    subject: str,
    description: str,
    status: str,
    amount: float = 0.0,
    created_by: str = "CRM User",
    db_path: str | Path = DEFAULT_DB_PATH,
) -> str:
    """Add a customer event and return the new event ID."""
    if event_type not in {"Call", "Email", "Ticket", "Purchase"}:
        raise ValueError("event_type must be Call, Email, Ticket, or Purchase")
    if not get_customer_profile(customer_id, db_path=db_path):
        raise ValueError(f"Unknown customer ID: {customer_id}")
    parsed_date = pd.to_datetime(event_date, errors="coerce")
    if pd.isna(parsed_date):
        raise ValueError("event_date must be a valid date and time")
    if not subject.strip():
        raise ValueError("subject cannot be empty")
    try:
        clean_amount = float(amount or 0.0)
    except (TypeError, ValueError) as exc:
        raise ValueError("amount must be a number") from exc
    if clean_amount < 0:
        raise ValueError("amount cannot be negative")
    normalized_date = parsed_date.strftime("%Y-%m-%d %H:%M")
    with get_connection(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM customer_events").fetchone()[0]
        event_id = f"EVT-{3000 + count + 1:04d}"
        # Avoid collisions if deleted/test records mean count-based IDs were reused.
        while conn.execute("SELECT 1 FROM customer_events WHERE event_id = ?", (event_id,)).fetchone():
            event_id = f"EVT-{int(event_id.split('-')[1]) + 1:04d}"
        conn.execute(
            """INSERT INTO customer_events
               (event_id, customer_id, event_type, event_date, subject, description, status, amount, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, customer_id, event_type, normalized_date, subject.strip(), description.strip(),
             status.strip() or "Completed", clean_amount, created_by.strip() or "CRM User"),
        )
    return event_id


def get_event_type_counts(customer_id: str, db_path: str | Path = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Return grouped event counts by type for simple reporting/visualization."""
    with get_connection(db_path) as conn:
        result = pd.read_sql_query(
            "SELECT event_type, COUNT(*) AS event_count FROM customer_events "
            "WHERE customer_id = ? GROUP BY event_type ORDER BY event_count DESC, event_type",
            conn,
            params=(customer_id,),
        )
    return result
