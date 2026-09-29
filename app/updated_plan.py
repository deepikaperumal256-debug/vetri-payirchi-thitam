from .config import get_settings
from .gemini_client import generate_text
from .gemini_generator import demo_workout
from .schemas import UserInput


def update_workout_plan(
    data: UserInput,
    original_plan: str,
    feedback: str,
) -> str:

    settings = get_settings()

    prompt = f"""
You are FitBuddy.

Update an existing 7-day wellness plan
based on user feedback.

USER PROFILE

Age:
{data.age}

Goal:
{data.goal}

Intensity:
{data.intensity}


ORIGINAL PLAN

{original_plan}


USER FEEDBACK

{feedback}


REQUIREMENTS

1. Return a complete revised Day 1-Day 7 plan.

2. Do not return only the changed section.

3. Keep the plan safe.

4. Keep recommendations age-appropriate.

5. Do not recommend extreme exercise.

6. Do not recommend restrictive eating.

7. Do not recommend supplements.

8. Do not provide medical treatment.

9. Do not diagnose health conditions.

10. Use supportive, non-appearance-focused language.

11. If the user is under 18, encourage parent/guardian
and qualified professional input.

Return plain text.
Do not use tables.
"""

    result = generate_text(
        prompt,
        settings.gemini_workout_model,
    )

    if not result:

        return (
            demo_workout(data)
            + "\n\n"
            + "DEMO UPDATE BASED ON USER FEEDBACK:\n"
            + feedback
        )

    return result