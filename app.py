# ------------------------------------------------------------
# Beginner Guide: Read this first
# ------------------------------------------------------------
# This app is the Streamlit frontend for your travel planner.
# It collects user inputs and calls the CrewAI workflow to generate reports.
#
# High-level flow of this file:
# 1) Import libraries and helper functions from crew_workflow.py
# 2) Configure Streamlit page settings
# 3) Add custom CSS styles for better UI design
# 4) Render the main form (from city, destination, dates, interests)
# 5) On submit, validate input and build a TripRequest object
# 6) Call run_trip_planner_crew(...) to execute agents
# 7) Show generated reports in tabs and save markdown files
#
# If you are new to Python:
# - Read this file from top to bottom once
# - Then run the app and map each UI section to the matching code block
# - Finally open crew_workflow.py to understand agent/task orchestration
# ------------------------------------------------------------

from datetime import date, timedelta

import streamlit as st

# These are your own project functions/classes from crew_workflow.py.
from crew_workflow import TripRequest, run_trip_planner_crew


# Configure the browser tab (title, icon, and layout width).
st.set_page_config(
    page_title="AI Trip Planner Assistant",
    page_icon="🧭",
    layout="wide",
)


# Inject custom CSS so the app looks like a polished product page.
# Streamlit allows HTML/CSS injection when unsafe_allow_html=True.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

    :root {
        --sand: #f6efe5;
        --paper: #fffaf3;
        --ink: #1f2a2c;
        --muted: #617173;
        --teal: #1d6f6d;
        --sea: #d9efec;
        --coral: #e57a61;
        --gold: #d9a441;
        --line: rgba(31, 42, 44, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(229, 122, 97, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(29, 111, 109, 0.18), transparent 32%),
            linear-gradient(180deg, #f9f4ec 0%, #f6efe5 45%, #f3ebdf 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--ink);
        letter-spacing: 0.01em;
    }

    p, label, div, span {
        font-family: 'Manrope', sans-serif !important;
    }

    .hero-shell {
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 2.25rem;
        background:
            linear-gradient(135deg, rgba(255, 250, 243, 0.96), rgba(255, 255, 255, 0.84)),
            linear-gradient(120deg, rgba(29, 111, 109, 0.08), rgba(229, 122, 97, 0.10));
        box-shadow: 0 18px 60px rgba(59, 70, 68, 0.08);
        margin-bottom: 1.25rem;
    }

    .eyebrow {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        background: rgba(29, 111, 109, 0.10);
        color: var(--teal);
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 4rem;
        line-height: 0.95;
        margin: 0;
        max-width: 700px;
    }

    .hero-copy {
        max-width: 720px;
        color: var(--muted);
        font-size: 1.03rem;
        line-height: 1.7;
        margin-top: 1rem;
        margin-bottom: 1.4rem;
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 1.4rem;
    }

    .stat-card, .info-card {
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.8);
        border-radius: 22px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(59, 70, 68, 0.05);
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .stat-value {
        color: var(--ink);
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }

    .section-title {
        font-size: 2.2rem;
        margin-top: 0.4rem;
        margin-bottom: 0.25rem;
    }

    .section-copy {
        color: var(--muted);
        margin-bottom: 1rem;
    }

    div[data-testid="stForm"] {
        border: 1px solid var(--line);
        border-radius: 26px;
        background: rgba(255, 255, 255, 0.72);
        padding: 1.1rem 1.2rem 0.5rem 1.2rem;
        box-shadow: 0 16px 40px rgba(59, 70, 68, 0.06);
    }

    div[data-testid="stDateInput"],
    div[data-testid="stTextInput"],
    div[data-testid="stMultiSelect"],
    div[data-testid="stTextArea"] {
        background: transparent;
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, var(--teal), #114f4e);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.75rem 1.2rem;
        font-weight: 700;
        box-shadow: 0 10px 24px rgba(29, 111, 109, 0.28);
    }

    .pill-row {
        display: flex;
        gap: 0.65rem;
        flex-wrap: wrap;
        margin-top: 0.9rem;
        margin-bottom: 0.2rem;
    }

    .pill {
        display: inline-block;
        padding: 0.5rem 0.8rem;
        border-radius: 999px;
        background: rgba(217, 164, 65, 0.14);
        color: #8d6513;
        font-size: 0.88rem;
        font-weight: 700;
    }

    .workflow-step {
        border-left: 4px solid var(--coral);
        padding: 0.3rem 0 0.3rem 1rem;
        margin-bottom: 1rem;
    }

    .workflow-step h4 {
        margin: 0;
        font-family: 'Manrope', sans-serif !important;
        color: var(--ink);
        font-size: 1rem;
    }

    .workflow-step p {
        margin: 0.2rem 0 0;
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .mini-note {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    @media (max-width: 900px) {
        .hero-title {
            font-size: 2.8rem;
        }

        .stat-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# This expander acts like an in-app mini tutorial for beginners.
with st.expander("New to Python? Click here for a quick code walkthrough"):
    st.markdown(
        """
        ### How this app works

        1. You fill the form with travel details.
        2. The app creates a TripRequest object from your input.
        3. The app calls run_trip_planner_crew(request).
        4. CrewAI runs agents in sequence:
           - Researcher Agent
           - Guide Expert Agent
           - Trip Planner Agent
        5. Reports are shown in the UI and also saved as files.

        ### Where to read next

        - app.py: UI + submit logic
        - crew_workflow.py: agents, tasks, fallback behavior, file saving
        """
    )


# Use today's date to set sensible default travel dates.
today = date.today()
default_departure = today + timedelta(days=14)
default_return = today + timedelta(days=20)

# Hero section at the top of the page.
st.markdown(
    """
    <section class="hero-shell">
        <div class="eyebrow">Travel Planning Studio</div>
        <h1 class="hero-title">Plan the trip first. Let the agents do the heavy lifting.</h1>
        <p class="hero-copy">
            This Streamlit app turns your travel brief into a clean planning experience.
            You choose the route, timing, and interests. The multi-agent workflow then converts
            those details into a destination report, local guide, and final itinerary.
        </p>
        <div class="pill-row">
            <span class="pill">Streamlit UI</span>
            <span class="pill">CrewAI Workflow</span>
            <span class="pill">Travel Research</span>
        </div>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-label">Planned Inputs</div>
                <div class="stat-value">5 Core Fields</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Agent Sequence</div>
                <div class="stat-value">3-Step Crew</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Generated Outputs</div>
                <div class="stat-value">3 Markdown Reports</div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Create two responsive columns:
# - Left: user form
# - Right: workflow explanation and output file info
form_col, detail_col = st.columns([1.45, 1], gap="large")

with form_col:
    # Section heading for the input area.
    st.markdown('<h2 class="section-title">Build Your Travel Brief</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-copy">Start with the essentials. This form is designed as the front door for your future AI trip planner.</p>',
        unsafe_allow_html=True,
    )

    # st.form groups inputs and only submits when the user clicks the button.
    with st.form("trip_planner_form"):
        # Split form into two columns for cleaner input layout.
        travel_col, timing_col = st.columns(2, gap="large")

        with travel_col:
            # Basic route details.
            from_city = st.text_input("From City", placeholder="e.g. Hyderabad")
            destination_city = st.text_input(
                "Destination City", placeholder="e.g. Paris"
            )
            # Multi-select lets users choose multiple interests.
            interests = st.multiselect(
                "Your Interests",
                options=[
                    "Sightseeing",
                    "Food",
                    "Adventure",
                    "Culture",
                    "Shopping",
                    "Nature",
                    "Nightlife",
                    "History",
                ],
                placeholder="Select what kind of trip you want",
            )

        with timing_col:
            # Date inputs with guard rails (min_value prevents invalid date choices).
            departure_date = st.date_input(
                "Departure Date",
                value=default_departure,
                min_value=today,
            )
            return_date = st.date_input(
                "Return Date",
                value=default_return,
                min_value=default_departure,
            )
            # Free text for additional user preferences.
            extra_notes = st.text_area(
                "Extra Notes",
                placeholder="Budget range, hotel preference, trip pace, family needs, or must-visit places",
                height=128,
            )

        # The form only sends values after this button is clicked.
        submitted = st.form_submit_button("Preview My Travel Plan")

with detail_col:
    # Side panel showing what your CrewAI pipeline does.
    st.markdown('<h2 class="section-title">Crew Preview</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-copy">This side panel shows the live CrewAI workflow used to generate your reports.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-card">
            <div class="workflow-step">
                <h4>Researcher Agent</h4>
                <p>Collects destination facts, local highlights, and essential travel context.</p>
            </div>
            <div class="workflow-step">
                <h4>Guide Expert Agent</h4>
                <p>Turns raw destination research into a practical city guide with useful recommendations.</p>
            </div>
            <div class="workflow-step">
                <h4>Trip Planner Agent</h4>
                <p>Combines timing, interests, and guide content into a complete travel itinerary.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Planned Output Files")
    output_a, output_b, output_c = st.columns(3)
    output_a.metric("Research", "city_report.md")
    output_b.metric("Guide", "guide_report.md")
    output_c.metric("Itinerary", "travel_plan.md")

    st.markdown(
        '<p class="mini-note">Live mode: form submission runs agents in sequence and writes city_report.md, guide_report.md, and travel_plan.md.</p>',
        unsafe_allow_html=True,
    )

# This block runs only after form submission.
if submitted:
    # Clean up spaces from user text input.
    from_city = from_city.strip()
    destination_city = destination_city.strip()

    # Basic validation: both cities are required for planning.
    if not from_city or not destination_city:
        st.error("Please enter both From City and Destination City.")
        st.stop()

    # Calculate trip length in days.
    trip_length = (return_date - departure_date).days
    st.markdown("### Run Summary")

    # Package all user inputs into a strongly-typed request object.
    request = TripRequest(
        from_city=from_city,
        destination_city=destination_city,
        departure_date=str(departure_date),
        return_date=str(return_date),
        interests=interests,
        extra_notes=extra_notes.strip(),
    )

    # Run the CrewAI workflow while showing a loading indicator in the UI.
    with st.spinner("Running CrewAI agents and generating reports..."):
        workflow_result = run_trip_planner_crew(request)

    # Two-column output: left = submitted input summary, right = file save confirmation.
    summary_col, outputs_col = st.columns([1.3, 1], gap="large")

    with summary_col:
        # If model execution fails, the workflow returns fallback reports safely.
        if workflow_result.used_fallback:
            st.warning(workflow_result.status_message)
        else:
            st.success(workflow_result.status_message)

        # Echo user inputs back for transparency and easy debugging.
        st.write(
            {
                "from_city": from_city,
                "destination_city": destination_city,
                "departure_date": str(departure_date),
                "return_date": str(return_date),
                "trip_length_days": trip_length,
                "interests": interests,
                "extra_notes": extra_notes,
            }
        )

    with outputs_col:
        # Confirmation that markdown files were written to disk.
        st.markdown("#### Generated Files")
        st.success("city_report.md saved")
        st.success("guide_report.md saved")
        st.success("travel_plan.md saved")

    # Show generated markdown content directly in tabs.
    st.markdown("### Generated Reports")
    tab_city, tab_guide, tab_plan = st.tabs(["City Report", "Guide Report", "Travel Plan"])

    with tab_city:
        st.markdown(workflow_result.city_report)

    with tab_guide:
        st.markdown(workflow_result.guide_report)

    with tab_plan:
        st.markdown(workflow_result.travel_plan)