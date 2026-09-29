from .config import get_settings
from .gemini_client import generate_text
from .schemas import UserInput


def demo_workout(
    data: UserInput,
) -> str:

    return f"""
FITBUDDY 7-DAY WELLNESS PLAN

Goal: {data.goal.title()}
Intensity: {data.intensity.title()}


DAY 1 - FULL BODY

Warm-up:
5-10 minutes of easy movement.

Main Workout:
• Bodyweight squats - 2 to 3 sets of 8-12
• Wall or incline push-ups - 2 to 3 sets of 8-12
• Glute bridges - 2 to 3 sets of 10-15

Cooldown:
5 minutes of gentle stretching.


DAY 2 - CARDIO AND MOBILITY

Warm-up:
5 minutes.

Main Workout:
20-30 minutes of comfortable walking or cycling.

Mobility:
Gentle shoulder, hip and ankle movements.

Cooldown:
Easy breathing and stretching.


DAY 3 - UPPER BODY AND CORE

Warm-up:
5-10 minutes.

Main Workout:
• Row variation - 2 to 3 sets of 8-12
• Shoulder movement - 2 to 3 sets of 8-12
• Dead bug - 2 to 3 sets of 6-10 per side

Cooldown:
Gentle stretching.


DAY 4 - RECOVERY

Take an easy walk or perform gentle mobility
for approximately 20-30 minutes.

Focus on recovery and sleep.


DAY 5 - LOWER BODY

Warm-up:
5-10 minutes.

Main Workout:
• Squat variation - 2 to 3 sets of 8-12
• Reverse lunge variation - 2 to 3 sets of 6-10 per side
• Calf raises - 2 to 3 sets of 10-15

Cooldown:
Gentle stretching.


DAY 6 - FUN ACTIVITY

Choose a safe activity you enjoy.

Examples:
• Walking
• Cycling
• Dancing
• Recreational activity

Keep the intensity comfortable.


DAY 7 - REST AND RECOVERY

Rest.

Focus on:
• Hydration
• Sleep
• Gentle mobility
• Recovery


SAFETY NOTE

Stop if you experience pain, dizziness,
or feel unwell.

For personalized exercise guidance,
especially for younger users or anyone
with health concerns, involve an appropriate
parent/guardian and qualified professional.
"""


def generate_workout_gemini(
    data: UserInput,
) -> str:

    settings = get_settings()

    prompt = f"""
You are FitBuddy, a cautious wellness assistant.

Create a structured 7-day general fitness
and wellness plan.

USER INFORMATION

Name: {data.username}

Age: {data.age}

Weight: {data.weight} kg

Goal: {data.goal}

Preferred intensity: {data.intensity}


REQUIREMENTS

1. Create Day 1 through Day 7.

2. Include a warm-up for active days.

3. Include the main activity.

4. Include cooldown or recovery guidance.

5. Give simple sets/repetitions or duration.

6. Include rest/recovery days.

7. Keep recommendations safe and realistic.

8. Do not recommend extreme exercise.

9. Do not recommend starvation or restrictive eating.

10. Do not prescribe supplements.

11. Do not diagnose medical conditions.

12. Use supportive language.

13. Do not focus on appearance.

14. If the user is under 18, keep the recommendations
age-appropriate and encourage involving a parent/guardian
and qualified professional for individualized guidance.

15. Return plain text.

16. Do not use a table.

The goal is to create a useful and easy-to-follow
weekly wellness plan.
"""

    result = generate_text(
        prompt,
        settings.gemini_workout_model,
    )

    # Demo fallback
    if not result:
        return demo_workout(data)

    return result