# Project Documentation: Customer Timeline Generator

## 1. Project Overview

**Project title:** Customer Timeline Generator  
**Project area:** Python + NLP + CRM project work  
**Project type:** Individual project  
**Planned duration:** Five days  
**Primary technologies:** Python, pandas, datetime, SQLite, sorting and grouping  
**User interface:** Streamlit

The Customer Timeline Generator is a CRM feature that collects customer interactions and displays them in chronological order. It consolidates calls, emails, service tickets, and purchases into a single customer history so a CRM user can understand the relationship and recent activity without checking separate records manually.

## 2. Abstract

Customer-facing teams often record interactions in separate modules or files. This makes it difficult to understand the complete history of an account quickly. The Customer Timeline Generator addresses this problem by storing customer profiles and interaction events in a SQLite database, retrieving events for a selected customer, sorting those events by date and time, and displaying them in a filterable CRM profile view. pandas is used to work with tabular event data; Python's date and time utilities normalize and display timestamps; SQLite provides persistent relational storage. The interface also supports adding interactions, viewing activity summaries, and exporting the filtered history to CSV.

## 3. Problem Statement

When customer calls, emails, tickets, and purchases are stored separately, users must search multiple places to reconstruct what happened and when. This can lead to slower service, missed follow-ups, and incomplete account context. A unified, chronological timeline provides one consistent view of customer activity.

## 4. Project Objectives

1. Define a structured schema for customers and customer events.
2. Create a realistic sample dataset that includes multiple customers and interaction types.
3. Retrieve all interaction events for a selected customer.
4. Sort interactions chronologically and keep the ordering deterministic when timestamps match.
5. Display the customer profile and history in a clear CRM-style interface.
6. Allow users to filter, search, add, inspect, and export interaction records.
7. Test the timeline logic with multiple customers and common edge cases.
8. Provide setup instructions, technical documentation, and demo screenshots.

## 5. Scope

### Included

- Customer profile data and event data.
- Calls, emails, tickets, and purchases.
- SQLite schema initialization and sample-data loading.
- Customer-specific event aggregation and chronological sorting.
- Date, event-type, and text filters.
- Summary metrics and grouped event counts.
- New-event entry and CSV export.
- Automated tests and documentation.

### Not included in this educational version

- User authentication or permission management.
- Integration with a real email, telephony, payment, or ticketing provider.
- Cloud hosting, multi-user synchronization, and production backups.
- Automated natural-language processing of unstructured emails or calls. The project belongs to a Python + NLP + CRM learning context, but the assigned objective focuses on event aggregation and timeline generation; NLP extraction can be an extension.

## 6. Technology Stack

| Technology | Role in the project |
|---|---|
| Python | Application logic, validation, and application entry point |
| pandas | CSV loading, tabular event handling, date parsing, sorting, and summaries |
| datetime | Date/time selection, timestamp normalization, and readable formatting |
| SQLite | Persistent storage for customer profiles and interaction events |
| SQL | Customer-specific retrieval, filtering, indexing, and grouped counts |
| Streamlit | Interactive CRM profile and timeline presentation |
| pytest | Automated unit testing |

## 7. System Workflow

```text
Select Customer ID
       ↓
Retrieve Customer Profile and Events from SQLite
       ↓
Apply Optional Date / Type / Text Filters
       ↓
Parse Dates and Sort by Event Date, then Event ID
       ↓
Calculate Activity Metrics and Group Counts
       ↓
Generate Chronological Timeline
       ↓
Display Customer History / Event Table / Summary
       ↓
Optional: Add Event or Export Filtered Timeline
```

## 8. Data Design

The database uses two related tables.

### 8.1 Customers table

| Field | Type | Description |
|---|---|---|
| customer_id | TEXT, Primary Key | Unique customer identifier |
| customer_name | TEXT | Customer name |
| email | TEXT | Contact email |
| phone | TEXT | Contact phone number |
| company | TEXT | Organization |
| segment | TEXT | Customer segment |
| joined_date | TEXT | Customer creation/join date |

### 8.2 Customer events table

| Field | Type | Description |
|---|---|---|
| event_id | TEXT, Primary Key | Unique event identifier |
| customer_id | TEXT, Foreign Key | Links the event to a customer |
| event_type | TEXT | Call, Email, Ticket, or Purchase |
| event_date | TEXT | Event timestamp in ISO-like format `YYYY-MM-DD HH:MM` |
| subject | TEXT | Short event title |
| description | TEXT | Event details |
| status | TEXT | Current event status |
| amount | REAL | Purchase amount; zero for other event types |
| created_by | TEXT | User/team that recorded the event |

The `customer_events` table has a foreign key to `customers`. An index on customer ID and event date helps the application retrieve one customer's events in chronological order efficiently. Timestamps use a consistent year-month-day format so database sorting is reliable.

## 9. Sample Dataset

The project includes five fictional customer profiles and 26 interaction records. The records cover all four event types and include historical and recent examples, completed events, sent emails, resolved tickets, open/pending tickets, and purchases with values. The CSV files are located in `data/` and are loaded into SQLite on first initialization.

Bundled records are demonstration data only and should not be interpreted as real customer information.

## 10. Core Algorithm

**Input:** A customer ID and optional filters.  
**Output:** An ordered collection of the customer's interaction events.

1. Connect to SQLite and verify that the database schema exists.
2. Read the selected customer's event rows using a parameterized SQL query.
3. Apply optional start-date, end-date, event-type, and text filters.
4. Load the result into a pandas DataFrame.
5. Convert the event timestamp column to datetime values.
6. Sort the rows in ascending order by `event_date`; use `event_id` as a secondary key for equal timestamps.
7. Calculate profile metrics such as calls, emails, tickets, open/pending tickets, and total purchase value.
8. Return the ordered result to the UI for rendering or CSV export.

### Simplified pseudocode

```text
FUNCTION generate_timeline(customer_id, filters):
    events = fetch_events_from_database(customer_id, filters)
    IF events is empty:
        RETURN empty list
    events.event_date = parse_datetime(events.event_date)
    events = sort(events, by=[event_date ASC, event_id ASC])
    RETURN events as a list of event records
```

## 11. Application Modules

### `timeline_generator.py`

Implements database initialization, seed-data import, customer lookup, event retrieval, chronological timeline generation, activity metrics, event-type grouping, and event insertion. The business logic is separate from the user interface so it can be tested and reused.

### `app.py`

Provides the Streamlit interface. The sidebar contains customer selection and filters, together with an add-interaction form. The main panel shows customer contact details, summary metrics, a timeline feed, a tabular record view, and an activity summary. Users can export the currently filtered events as a CSV file.

### `data/customers.csv` and `data/customer_events.csv`

Provide the seed dataset used to initialize a new local database.

### `tests/test_timeline_generator.py`

Checks database initialization, chronological sorting, customer isolation, filtering, inclusive date ranges, summary calculations, successful event insertion, invalid customers, negative purchase amounts, and unknown customer handling.

## 12. Validation and Test Plan

| Test case | Expected result |
|---|---|
| Initialize a fresh database | Tables and fictional seed records are created |
| Select a known customer | Only that customer's profile and events are returned |
| Generate timeline | Events are sorted oldest to newest |
| Two events have same timestamp | `event_id` provides a deterministic tie-breaker |
| Filter by event type | Only the selected types are returned |
| Filter by date interval | Start and end dates are included |
| Search for a keyword | Matching subject, description, or status rows are returned |
| Add a valid event | A new event ID is returned and the record appears in the timeline |
| Add event for unknown customer | Validation error is raised |
| Add negative purchase amount | Validation error is raised |
| Customer has no matching rows | An empty result is returned and the UI displays an empty state |

Execute the automated checks with `python -m pytest -q` after installing the dependencies.

## 13. Five-Day Implementation Plan

| Day | Planned work | Deliverable |
|---|---|---|
| Day 1 | Define customer/event schema and prepare sample records | CSV dataset and SQLite schema |
| Day 2 | Implement event retrieval, aggregation, date parsing, sorting, and grouping | Timeline generator module |
| Day 3 | Build the customer profile and timeline screen; validate multiple customers | Streamlit CRM interface |
| Day 4 | Add filters, event entry, CSV export, error handling, and tests | Functional workflow and test suite |
| Day 5 | Complete documentation, capture demo images, run final verification | README, project report, screenshots, and packaged project |

## 14. How to Run the Project

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Run `python -m streamlit run app.py`.
5. Open the local URL printed by Streamlit.
6. Select a customer and explore their timeline. To test persistence, add a new interaction and refresh or switch tabs.
7. Run `python -m pytest -q` to execute the unit tests.

See `README.md` for platform-specific installation instructions and troubleshooting.

## 15. Screenshots and Demo Evidence

The `screenshots/` directory includes two illustrative previews based on the bundled fictional data: `crm_timeline_demo.png` shows the customer profile, metrics, filters, and timeline feed; `sample_timeline_output.png` shows a table-style event-record view with seven chronologically ordered records. These are design previews rather than screenshots captured from a running Streamlit session. Launch `app.py` locally to interact with the actual application.

## 16. Expected Outcome

The user can select any sample customer and view one chronological history containing the available calls, emails, support tickets, and purchases. Summary metrics indicate account activity at a glance. Filters help narrow the history, and the interface supports adding new events and downloading the current view. Tests verify the main data and timeline behavior.

## 17. Future Enhancements

- Add text classification to categorize incoming emails and call notes.
- Use named-entity recognition to identify products, dates, people, or issues in interaction descriptions.
- Summarize long histories with an NLP or language-model component.
- Add reminders for open tickets and overdue follow-ups.
- Integrate CRM, email, telephony, and ticket-system APIs.
- Add authentication, permissions, audit trails, and database backup strategies for production use.
- Add customer segmentation and trend analysis over time.

## 18. Conclusion

The Customer Timeline Generator demonstrates a practical CRM workflow using Python, pandas, datetime, SQLite, and sorting/grouping techniques. A normalized data model connects interactions to customer profiles; a deterministic chronological sort turns event rows into a readable history; and the Streamlit UI makes the result accessible to a user. The included sample data, tests, README, formal documentation, and demo screenshots make the project suitable for a classroom demonstration and further extension.
