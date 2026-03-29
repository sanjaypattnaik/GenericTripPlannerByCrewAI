"""High-level CrewAI workflow for the travel planner app.

This module keeps agent orchestration separate from the UI layer so the Streamlit
app can stay clean and focused on user experience.

Beginner note:
- app.py is the UI layer (what user sees)
- this file is the workflow layer (what generates reports)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from crewai import Agent, Crew, LLM, Process, Task


# dataclass gives us a clean "container" for input fields.
# It reduces manual __init__ code and keeps types clear.
@dataclass
class TripRequest:
    # City the user starts from.
    from_city: str
    # City the user wants to visit.
    destination_city: str
    # Dates are kept as string for easier prompt building and serialization.
    departure_date: str
    return_date: str
    # List of interests selected in the UI.
    interests: list[str]
    # Optional free-text notes.
    extra_notes: str


# Output object returned to the UI after workflow execution.
@dataclass
class TripResult:
    # Full markdown content for each report.
    city_report: str
    guide_report: str
    travel_plan: str
    # True means we used fallback report generation instead of live LLM output.
    used_fallback: bool
    # Human-readable status displayed in Streamlit.
    status_message: str


def _write_report(file_path: Path, content: str) -> None:
    """Write one markdown report to disk.

    .strip() removes accidental leading/trailing empty lines.
    + "\n" ensures each file ends with a newline (good file hygiene).
    """
    file_path.write_text(content.strip() + "\n", encoding="utf-8")


def _persist_reports(base_dir: Path, result: TripResult) -> None:
    """Save all three generated reports as markdown files."""
    _write_report(base_dir / "city_report.md", result.city_report)
    _write_report(base_dir / "guide_report.md", result.guide_report)
    _write_report(base_dir / "travel_plan.md", result.travel_plan)


def _build_fallback_result(request: TripRequest, reason: str) -> TripResult:
    """Build deterministic reports when live LLM execution fails.

    This keeps the app reliable for beginners even if model setup is incomplete.
    """
    # Convert list of interests to readable text.
    interests_text = ", ".join(request.interests) if request.interests else "General"

    # Basic but structured fallback city report.
    city_report = f"""# City Report: {request.destination_city}

## Overview
{request.destination_city} is prepared as the selected destination for this trip from {request.from_city}.

## Travel Window
- Departure: {request.departure_date}
- Return: {request.return_date}

## Interest Focus
{interests_text}

## Notes
{request.extra_notes or 'No additional notes provided.'}
"""

    # Basic but structured fallback guide report.
    guide_report = f"""# Guide Report: {request.destination_city}

## Suggested Focus Areas
- Top neighborhoods and landmarks
- Food recommendations aligned to selected interests
- Local transport and practical travel tips

## Personalized Angle
Primary preferences: {interests_text}
"""

    # Basic but structured fallback itinerary.
    travel_plan = f"""# Travel Plan: {request.from_city} -> {request.destination_city}

## Trip Summary
- Route: {request.from_city} to {request.destination_city}
- Dates: {request.departure_date} to {request.return_date}
- Interests: {interests_text}

## Draft Itinerary Structure
1. Day 1: Arrival and local orientation
2. Day 2: Main highlights and culture
3. Day 3: Food and local exploration
4. Day 4: Flexible recommendations based on pace and budget

## Planner Notes
{request.extra_notes or 'No additional notes provided.'}
"""

    # Return a complete result object marked as fallback.
    return TripResult(
        city_report=city_report,
        guide_report=guide_report,
        travel_plan=travel_plan,
        used_fallback=True,
        status_message=(
            "CrewAI live run was unavailable. Generated structured fallback reports instead. "
            f"Reason: {reason}"
        ),
    )


def _build_llm() -> LLM:
    """Create the LLM configuration used by all agents.

    Default model is Ollama + llama3.2. You can override model/base URL by env vars:
    - TRIP_PLANNER_MODEL
    - OLLAMA_BASE_URL
    """
    # Default to a model name that is commonly available after standard Ollama setup.
    model_name = os.getenv("TRIP_PLANNER_MODEL", "ollama/llama3:latest")
    llm_kwargs: dict[str, str] = {"model": model_name}

    # If model uses Ollama provider, set the Ollama server URL.
    if model_name.startswith("ollama/"):
        llm_kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Construct CrewAI LLM instance from collected kwargs.
    return LLM(**llm_kwargs)


def run_trip_planner_crew(request: TripRequest, report_dir: str | Path = ".") -> TripResult:
    """Run the sequential travel planning crew and save markdown reports.

    High-level flow:
    1) Build LLM
    2) Build agents
    3) Build tasks with dependencies (context)
    4) Run crew sequentially
    5) Save outputs to disk
    6) On any error, generate fallback output
    """
    # Normalize output directory to Path object.
    output_dir = Path(report_dir)

    # try/except keeps app resilient for beginner workflows.
    try:
        # Build shared language model config used by all agents.
        llm = _build_llm()
        # Human-readable interests string used inside task prompts.
        interests_text = ", ".join(request.interests) if request.interests else "General"

        # Agent 1: collects destination research.
        researcher_agent = Agent(
            role="City Researcher",
            goal="Collect high-value local context for the selected destination.",
            backstory="A seasoned destination analyst focused on practical, traveler-friendly insights.",
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        # Agent 2: turns research into practical guide content.
        guide_expert_agent = Agent(
            role="Guide Expert",
            goal="Transform destination research into a concise and actionable city guide.",
            backstory="A local guide specialist who translates research into useful recommendations.",
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        # Agent 3: creates final itinerary using previous context.
        planner_agent = Agent(
            role="Trip Planner Expert",
            goal="Create a coherent itinerary matched to dates and traveler interests.",
            backstory="An itinerary strategist balancing practicality, experience quality, and user preferences.",
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )

        # Task 1 (research) has no upstream context.
        location_task = Task(
            description=(
                f"Create a city research report for {request.destination_city}. "
                f"Traveler is departing from {request.from_city}. "
                f"Travel window: {request.departure_date} to {request.return_date}. "
                f"Interests: {interests_text}. "
                f"Additional notes: {request.extra_notes or 'None'}. "
                "Return a concise markdown report with sections: Overview, Must-See Areas, Local Tips, and Best Fit for Interests."
            ),
            expected_output="A markdown-formatted city report with practical local insights.",
            agent=researcher_agent,
        )

        # Task 2 (guide) depends on Task 1 output.
        guide_task = Task(
            description=(
                f"Using the city research for {request.destination_city}, produce a practical guide report. "
                "Include food, transport, neighborhood recommendations, and travel pacing advice."
            ),
            expected_output="A markdown-formatted guide report tailored to traveler preferences.",
            agent=guide_expert_agent,
            context=[location_task],
        )

        # Task 3 (plan) depends on Task 1 + Task 2 outputs.
        planner_task = Task(
            description=(
                f"Create a complete trip plan from {request.from_city} to {request.destination_city} "
                f"for {request.departure_date} to {request.return_date}. "
                "Use prior research and guide results to build a day-wise itinerary with practical notes."
            ),
            expected_output="A markdown-formatted day-by-day travel plan.",
            agent=planner_agent,
            context=[location_task, guide_task],
        )

        # Process.sequential means tasks run in order, not parallel.
        crew = Crew(
            agents=[researcher_agent, guide_expert_agent, planner_agent],
            tasks=[location_task, guide_task, planner_task],
            process=Process.sequential,
            verbose=False,
        )

        # Execute full workflow.
        crew_result = crew.kickoff()

        # Prefer each task's raw output; provide default text if missing.
        city_report = (
            location_task.output.raw
            if location_task.output and location_task.output.raw
            else "# City Report\n\nNo city report content was generated."
        )
        guide_report = (
            guide_task.output.raw
            if guide_task.output and guide_task.output.raw
            else "# Guide Report\n\nNo guide report content was generated."
        )
        travel_plan = (
            planner_task.output.raw
            if planner_task.output and planner_task.output.raw
            else str(crew_result)
        )

        # Build result object for UI and file persistence.
        result = TripResult(
            city_report=city_report,
            guide_report=guide_report,
            travel_plan=travel_plan,
            used_fallback=False,
            status_message="CrewAI workflow completed successfully.",
        )

        # Save all report files and return success result.
        _persist_reports(output_dir, result)
        return result

    except Exception as exc:
        # Any error here will still produce readable fallback reports.
        fallback = _build_fallback_result(request, str(exc))
        _persist_reports(output_dir, fallback)
        return fallback