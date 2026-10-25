<<<<<<< HEAD
# Customer Timeline Generator

A lightweight CRM feature that presents a customer's calls, emails, support tickets, and purchases in one chronological history. The project uses Python, pandas, `datetime`, SQLite, and sorting/grouping, as required by the assignment.

> **Demo data notice:** All names, email addresses, phone numbers, companies, and interactions bundled with the project are fictional sample records.

## Features

- SQLite database with separate `customers` and `customer_events` tables.
- Automatically initializes the schema and loads CSV sample data on the first run.
- Customer profile view with contact details and activity metrics.
- Chronological timeline, with stable sorting by event date and event ID.
- Filters by date range and event type, plus text search across subject, description, and status.
- Add a call, email, ticket, or purchase from the sidebar; new events are saved to SQLite.
- View the underlying event records and activity counts by type.
- Export the filtered timeline to CSV.
- Unit tests for sorting, filters, summaries, adding events, and invalid input.

## Project structure

```text
customer_timeline_generator/
├── app.py                         # Streamlit CRM profile and timeline UI
├── timeline_generator.py          # SQLite, pandas and timeline business logic
├── requirements.txt               # Python dependencies
├── README.md                      # Setup and usage guide
├── PROJECT_DOCUMENTATION.md       # Formal project report
├── data/
│   ├── customers.csv               # Sample customer profile data
│   └── customer_events.csv         # Sample interactions across customers
├── tests/
│   └── test_timeline_generator.py  # Automated unit tests
└── screenshots/
    ├── crm_timeline_demo.png       # Example application preview
    └── sample_timeline_output.png  # Example sorted timeline output
```

The SQLite database `crm_timeline.db` is created in the project directory the first time the application or data module initializes. It is intentionally excluded from the ZIP so it can be created cleanly on each machine.

## Requirements

- Python 3.10 or newer
- pip
- Internet access for the first-time package installation

## Installation

Open PowerShell or a terminal in this project directory.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks script activation, use `\.venv\Scripts\python.exe -m pip install -r requirements.txt` and run the app with `\.venv\Scripts\python.exe -m streamlit run app.py`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the application

```bash
python -m streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open that URL in your browser.

## How to use

1. Choose a customer in the left-hand sidebar.
2. Review the customer profile and summary metrics.
3. Use the date, event-type, and search filters to narrow the timeline.
4. Open the **Timeline** tab for a chronological event feed.
5. Open **Event records** to inspect rows, or **Activity summary** to review the event counts.
6. Use **Download timeline CSV** to export the currently filtered timeline.
7. Expand **Add customer interaction**, complete the form, and click **Save interaction**. The event is saved to SQLite and appears in the timeline after refresh.

## Run tests

Install the requirements and run:

```bash
python -m pytest -q
```

The tests create an isolated temporary database, so the test records do not alter the application's database.

## Use the business logic without the UI

```python
from timeline_generator import init_db, generate_timeline, get_customer_summary

init_db()  # Creates crm_timeline.db and loads the sample CSV data once.
for event in generate_timeline("CUST-1001"):
    print(event["event_date"], event["event_type"], event["subject"])

print(get_customer_summary("CUST-1001"))
```

## Database schema

### `customers`

| Column | Purpose |
|---|---|
| `customer_id` | Primary key, for example `CUST-1001` |
| `customer_name` | Customer's display name |
| `email`, `phone` | Contact details |
| `company` | Organization name |
| `segment` | Enterprise, Mid-Market, or SMB segment |
| `joined_date` | Date the customer joined the CRM |

### `customer_events`

| Column | Purpose |
|---|---|
| `event_id` | Unique interaction ID |
| `customer_id` | Foreign key to `customers` |
| `event_type` | Call, Email, Ticket, or Purchase |
| `event_date` | Interaction date/time stored in `YYYY-MM-DD HH:MM` form |
| `subject`, `description` | Event title and details |
| `status` | Event status, such as Completed, Sent, Open, Pending, or Resolved |
| `amount` | Purchase amount; zero for non-purchase events |
| `created_by` | Person/team that logged the event |

An index on `(customer_id, event_date)` supports fast customer-specific timeline retrieval and chronological sorting.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'streamlit'`** — activate the virtual environment and run `pip install -r requirements.txt`.
- **Port 8501 is already in use** — run `python -m streamlit run app.py --server.port 8502`.
- **Sample data does not appear** — stop the app and verify that both CSV files exist in `data/`. For a fresh sample database, close the app and delete `crm_timeline.db`; the app recreates it from the bundled CSV files on the next run. Deleting the database permanently removes locally added events.
- **Timeline looks empty** — check the selected customer and remove restrictive filters.

## Scope and limitations

This is an educational prototype, not a production CRM. It has no authentication, role-based access, cloud synchronization, audit logging, or backup process. Do not put real customer data into a public demo without adding appropriate privacy, security, and access controls.

## Screenshots / demo

The `screenshots/` directory contains two illustrative UI previews based on the bundled fictional sample data: a CRM timeline view and a structured event-records view. They are design previews, not captures from a running Streamlit process. Run the application locally to interact with the live controls.
=======
# customer_timeline_generator
customer_timeline_generator Project 
>>>>>>> 1786441732236dd435aef0eb586761c276d20a34
