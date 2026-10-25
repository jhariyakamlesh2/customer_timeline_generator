"""Streamlit CRM interface for Customer Timeline Generator."""
from __future__ import annotations

import html
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd
import streamlit as st

from timeline_generator import (
    DEFAULT_DB_PATH,
    add_event,
    get_customer_events,
    get_customer_profile,
    get_customer_summary,
    get_customers,
    get_event_type_counts,
    init_db,
)

st.set_page_config(
    page_title="Customer Timeline Generator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# Compact, responsive styling for the CRM interface.
st.markdown(
    """
    <style>
      .stApp { background: #f5f7fb; }
      [data-testid="stHeader"] { background: rgba(245,247,251,.92); }
      .block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1450px; }
      .hero { background: linear-gradient(110deg,#152e55,#245b81); color: white; padding: 1.35rem 1.6rem; border-radius: 16px; margin-bottom: 1.1rem; }
      .hero h1 { font-size: 1.8rem; line-height: 1.2; margin: 0; color: white; }
      .hero p { margin: .45rem 0 0; color: #dbeafe; font-size: .95rem; }
      .profile-card { background: white; border: 1px solid #e5eaf2; border-radius: 14px; padding: 1.15rem 1.25rem; margin-bottom: 1rem; }
      .profile-name { color: #152e55; font-size: 1.45rem; font-weight: 750; margin: 0 0 .2rem 0; }
      .profile-meta { color: #64748b; font-size: .9rem; margin: .12rem 0; }
      .pill { display: inline-block; background: #eaf2ff; color: #2256a5; padding: .18rem .55rem; border-radius: 50px; font-size: .76rem; font-weight: 700; margin-left: .3rem; }
      .timeline-wrap { background: white; border: 1px solid #e5eaf2; border-radius: 14px; padding: .8rem 1rem; }
      .timeline-item { display: flex; gap: .9rem; padding: 1rem .25rem; border-bottom: 1px solid #edf1f6; }
      .timeline-item:last-child { border-bottom: 0; }
      .timeline-dot { min-width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
      .dot-call { background: #eaf2ff; } .dot-email { background: #e8f8f0; } .dot-ticket { background: #fff4df; } .dot-purchase { background: #f2eaff; }
      .timeline-content { flex: 1; min-width: 0; }
      .timeline-head { display: flex; flex-wrap: wrap; align-items: center; gap: .45rem; margin-bottom: .25rem; }
      .timeline-subject { color: #152e55; font-size: 1rem; font-weight: 720; }
      .event-chip { font-size: .7rem; font-weight: 750; padding: .14rem .48rem; border-radius: 5px; background: #f1f5f9; color: #334155; }
      .timeline-date { color: #64748b; font-size: .8rem; }
      .timeline-desc { color: #475569; font-size: .9rem; line-height: 1.5; margin: .45rem 0; }
      .timeline-foot { color: #64748b; font-size: .78rem; }
      .empty-state { padding: 2rem; text-align: center; color: #64748b; }
      div[data-testid="stMetric"] { background: white; border: 1px solid #e5eaf2; border-radius: 12px; padding: .8rem 1rem; }
      section[data-testid="stSidebar"] { background: #eef2f8; }
      .small-note { font-size: .8rem; color: #64748b; }
    </style>
    """,
    unsafe_allow_html=True,
)

EVENT_ICONS = {"Call": "📞", "Email": "✉️", "Ticket": "🎫", "Purchase": "🛍️"}
EVENT_DOTS = {"Call": "dot-call", "Email": "dot-email", "Ticket": "dot-ticket", "Purchase": "dot-purchase"}


def safe(value: object) -> str:
    """Escape user-controlled text before embedding it in HTML."""
    if value is None or pd.isna(value):
        return ""
    return html.escape(str(value))


def render_timeline(events: pd.DataFrame) -> None:
    if events.empty:
        st.markdown(
            '<div class="timeline-wrap"><div class="empty-state">'
            '<div style="font-size:2rem">🗂️</div><h3>No interactions found</h3>'
            '<p>Try changing the date range, event type, or search term.</p></div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="timeline-wrap">', unsafe_allow_html=True)
    for _, event in events.iterrows():
        event_type = str(event.get("event_type", "Event"))
        icon = EVENT_ICONS.get(event_type, "📝")
        dot_class = EVENT_DOTS.get(event_type, "dot-call")
        event_date = event.get("event_date")
        date_text = event_date.strftime("%d %b %Y · %I:%M %p") if pd.notna(event_date) else "Date not set"
        amount = float(event.get("amount", 0) or 0)
        purchase_text = f" · ₹{amount:,.2f}" if event_type == "Purchase" and amount else ""
        st.markdown(
            f'''<div class="timeline-item">
              <div class="timeline-dot {dot_class}">{icon}</div>
              <div class="timeline-content">
                <div class="timeline-head">
                  <span class="timeline-subject">{safe(event.get('subject'))}</span>
                  <span class="event-chip">{safe(event_type)}</span>
                  <span class="event-chip">{safe(event.get('status'))}</span>
                </div>
                <div class="timeline-date">{safe(date_text)}{safe(purchase_text)}</div>
                <div class="timeline-desc">{safe(event.get('description'))}</div>
                <div class="timeline-foot">Event ID: {safe(event.get('event_id'))} &nbsp; · &nbsp; Logged by {safe(event.get('created_by'))}</div>
              </div>
            </div>''',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


customers = get_customers()
if customers.empty:
    st.error("No customer records were found. Check the database setup and sample CSV files.")
    st.stop()

st.markdown(
    '<div class="hero"><h1>🧭 Customer Timeline Generator</h1>'
    '<p>A chronological view of customer calls, emails, support tickets, and purchases.</p></div>',
    unsafe_allow_html=True,
)

# Sidebar filters and quick-add form.
with st.sidebar:
    st.markdown("## Customer workspace")
    customer_options = {
        f"{row.customer_name} · {row.customer_id}": row.customer_id
        for row in customers.itertuples(index=False)
    }
    selected_label = st.selectbox("Select customer", list(customer_options.keys()))
    customer_id = customer_options[selected_label]

    st.markdown("---")
    st.markdown("### Timeline filters")
    range_mode = st.radio("Date range", ["All dates", "Custom range"], horizontal=False)
    start_date = end_date = None
    if range_mode == "Custom range":
        date_bounds = st.date_input(
            "Choose start and end dates",
            value=(date(2026, 1, 1), date.today()),
            help="Select both a start date and an end date.",
        )
        if isinstance(date_bounds, (tuple, list)) and len(date_bounds) == 2:
            start_date, end_date = date_bounds
            if start_date > end_date:
                st.warning("Start date must be on or before end date.")
                start_date = end_date = None

    selected_types = st.multiselect(
        "Event types",
        options=["Call", "Email", "Ticket", "Purchase"],
        default=["Call", "Email", "Ticket", "Purchase"],
    )
    search_text = st.text_input("Search subject, description, or status", placeholder="e.g. renewal")

    st.markdown("---")
    with st.expander("＋ Add customer interaction", expanded=False):
        with st.form("add_event_form", clear_on_submit=True):
            new_type = st.selectbox("Interaction type", ["Call", "Email", "Ticket", "Purchase"])
            new_date = st.date_input("Interaction date", value=date.today())
            new_time = st.time_input("Interaction time", value=time(10, 0))
            new_subject = st.text_input("Subject *", placeholder="Brief interaction title")
            new_description = st.text_area("Description", placeholder="What happened?", height=90)
            new_status = st.selectbox("Status", ["Completed", "Sent", "Open", "Pending", "Resolved", "Cancelled"])
            new_amount = st.number_input("Purchase amount (₹)", min_value=0.0, value=0.0, step=500.0,
                                         disabled=(new_type != "Purchase"))
            new_owner = st.text_input("Logged by", value="CRM User")
            submitted = st.form_submit_button("Save interaction", use_container_width=True)
            if submitted:
                try:
                    event_id = add_event(
                        customer_id=customer_id,
                        event_type=new_type,
                        event_date=datetime.combine(new_date, new_time).strftime("%Y-%m-%d %H:%M"),
                        subject=new_subject,
                        description=new_description,
                        status=new_status,
                        amount=new_amount if new_type == "Purchase" else 0.0,
                        created_by=new_owner,
                        db_path=DEFAULT_DB_PATH,
                    )
                    st.success(f"Saved interaction {event_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save interaction: {exc}")

profile = get_customer_profile(customer_id)
summary = get_customer_summary(customer_id)

# Customer identity card.
st.markdown(
    f'''<div class="profile-card">
      <div class="profile-name">{safe(profile['customer_name'])}<span class="pill">{safe(profile['segment'])}</span></div>
      <div class="profile-meta">{safe(profile['company'])} &nbsp; · &nbsp; Customer ID: {safe(profile['customer_id'])}</div>
      <div class="profile-meta">✉️ {safe(profile['email'])} &nbsp; · &nbsp; ☎️ {safe(profile['phone'])}</div>
      <div class="profile-meta">Customer since {safe(pd.to_datetime(profile['joined_date']).strftime('%d %b %Y'))}</div>
    </div>''',
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total interactions", f"{int(summary['total_events']):,}")
m2.metric("Calls", f"{int(summary['calls']):,}")
m3.metric("Emails", f"{int(summary['emails']):,}")
m4.metric("Open / pending tickets", f"{int(summary['open_tickets']):,}")
m5.metric("Purchase value", f"₹{float(summary['purchase_value']):,.0f}")

st.markdown("### Customer history")
filtered_events = get_customer_events(
    customer_id,
    start_date=start_date.isoformat() if start_date else None,
    end_date=end_date.isoformat() if end_date else None,
    event_types=selected_types,
    search_text=search_text,
)

left, right = st.columns([3, 1])
with left:
    st.caption(f"Showing {len(filtered_events)} matching interactions · Oldest to newest")
with right:
    if not filtered_events.empty:
        export_df = filtered_events.copy()
        export_df["event_date"] = export_df["event_date"].dt.strftime("%Y-%m-%d %H:%M")
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download timeline CSV",
            data=csv_data,
            file_name=f"{customer_id.lower()}_timeline.csv",
            mime="text/csv",
            use_container_width=True,
        )

view_timeline, view_table, view_summary = st.tabs(["🕒 Timeline", "📋 Event records", "📊 Activity summary"])
with view_timeline:
    render_timeline(filtered_events)

with view_table:
    if filtered_events.empty:
        st.info("No records match the current filters.")
    else:
        display_df = filtered_events.copy()
        display_df["event_date"] = display_df["event_date"].dt.strftime("%d %b %Y, %I:%M %p")
        display_df["amount"] = display_df.apply(
            lambda row: f"₹{row['amount']:,.2f}" if row["event_type"] == "Purchase" else "—", axis=1
        )
        display_df = display_df.rename(columns={
            "event_id": "Event ID", "event_type": "Type", "event_date": "Date & time",
            "subject": "Subject", "description": "Description", "status": "Status",
            "amount": "Amount", "created_by": "Logged by",
        })
        st.dataframe(
            display_df[["Event ID", "Type", "Date & time", "Subject", "Description", "Status", "Amount", "Logged by"]],
            use_container_width=True, hide_index=True,
        )

with view_summary:
    counts = get_event_type_counts(customer_id)
    if counts.empty:
        st.info("No activity summary is available yet.")
    else:
        col_chart, col_info = st.columns([3, 2])
        with col_chart:
            st.markdown("#### Interactions by type")
            chart_data = counts.set_index("event_type")["event_count"]
            st.bar_chart(chart_data, height=300)
        with col_info:
            st.markdown("#### Full account activity")
            st.dataframe(counts.rename(columns={"event_type": "Event type", "event_count": "Count"}),
                         hide_index=True, use_container_width=True)
            st.caption("Purchase value is calculated from events recorded as Purchase.")

st.markdown("---")
st.markdown(
    '<div class="small-note">Customer Timeline Generator · Python · pandas · datetime · SQLite · Sample data is fictional and for demonstration only.</div>',
    unsafe_allow_html=True,
)
