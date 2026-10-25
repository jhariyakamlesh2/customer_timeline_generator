"""Unit tests for Customer Timeline Generator business logic."""
from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from timeline_generator import (
    add_event,
    generate_timeline,
    get_customer_events,
    get_customer_profile,
    get_customer_summary,
    init_db,
)


@pytest.fixture
def database(tmp_path):
    db_path = tmp_path / "test_crm.db"
    init_db(db_path=db_path, seed=True)
    return db_path


def test_database_seeds_sample_customers_and_events(database):
    assert get_customer_profile("CUST-1001", db_path=database)["customer_name"] == "Aarav Sharma"
    events = get_customer_events("CUST-1001", db_path=database)
    assert len(events) >= 1


def test_timeline_is_chronological(database):
    timeline = generate_timeline("CUST-1001", db_path=database)
    dates = [event["event_date"] for event in timeline]
    assert dates == sorted(dates)
    assert len(timeline) == 7


def test_customer_filter_does_not_mix_events(database):
    events = get_customer_events("CUST-1002", db_path=database)
    assert not events.empty
    assert set(events["customer_id"]) == {"CUST-1002"}


def test_filter_by_type_and_text(database):
    events = get_customer_events("CUST-1001", db_path=database, event_types=["Ticket"], search_text="dashboard")
    assert len(events) == 1
    assert events.iloc[0]["subject"] == "Dashboard access request"


def test_date_filter_is_inclusive(database):
    events = get_customer_events(
        "CUST-1001", db_path=database, start_date="2026-10-18", end_date="2026-10-22"
    )
    assert len(events) == 2
    assert events["event_date"].min().date().isoformat() == "2026-10-18"
    assert events["event_date"].max().date().isoformat() == "2026-10-22"


def test_summary_metrics(database):
    summary = get_customer_summary("CUST-1001", db_path=database)
    assert summary["total_events"] == 7
    assert summary["calls"] == 2
    assert summary["emails"] == 2
    assert summary["tickets"] == 2
    assert summary["purchases"] == 1
    assert summary["purchase_value"] == 48000.0
    assert summary["open_tickets"] == 1


def test_add_event_appears_in_chronological_timeline(database):
    event_id = add_event(
        customer_id="CUST-1002",
        event_type="Call",
        event_date="2026-10-24 10:30",
        subject="Follow-up call",
        description="Checked implementation progress.",
        status="Completed",
        created_by="QA Test",
        db_path=database,
    )
    timeline = generate_timeline("CUST-1002", db_path=database)
    assert any(event["event_id"] == event_id for event in timeline)
    assert timeline[-1]["subject"] == "Follow-up call"


def test_add_event_rejects_unknown_customer(database):
    with pytest.raises(ValueError, match="Unknown customer ID"):
        add_event(
            customer_id="DOES-NOT-EXIST", event_type="Call", event_date="2026-10-24 10:00",
            subject="Test", description="", status="Completed", db_path=database,
        )


def test_add_event_rejects_negative_amount(database):
    with pytest.raises(ValueError, match="negative"):
        add_event(
            customer_id="CUST-1001", event_type="Purchase", event_date="2026-10-24 10:00",
            subject="Test purchase", description="", status="Completed", amount=-1, db_path=database,
        )


def test_unknown_customer_has_no_profile(database):
    assert get_customer_profile("INVALID-ID", db_path=database) is None


def test_empty_event_type_selection_returns_no_events(database):
    events = get_customer_events("CUST-1001", db_path=database, event_types=[])
    assert events.empty
