from .config import get_settings
from .gemini_client import generate_text
from .schemas import UserInput


def demo_tip(
    data: UserInput,
) -> str:

    tips = {

        "weight loss":
            "Focus on regular balanced meals, hydration, sleep, "
            "and enjoyable physical activity rather than restrictive dieting.",

        "muscle gain":
            "Include balanced meals with protein-rich foods and "
            "carbohydrates after activity, and prioritize recovery.",

        "general wellness":
            "Build a simple routine around regular movement, "
            "hydration, balanced meals, and enough sleep.",

        "flexibility":
            "Stay hydrated and combine gentle mobility work "
            "with gradual and comfortable movement.",
    }

    return tips[data.goal]


def generate_nutrition_tip_with_flash(
    data: UserInput,
) -> str:

    settings = get_settings()

    prompt = f"""
You are FitBuddy.

Give ONE concise nutrition or recovery tip.

Fitness goal:
{data.goal}

Workout intensity:
{data.intensity}

Requirements:

• Maximum 80 words.
• Make it practical.
• Keep it food-neutral and health-oriented.
• Do not recommend restrictive dieting.
• Do not recommend starvation.
• Do not prescribe supplements.
• Do not diagnose medical conditions.
• Focus on healthy habits and recovery.

If the person is under 18,
recommend involving a parent/guardian or qualified
professional for individualized nutrition advice.
"""

    result = generate_text(
        prompt,
        settings.gemini_nutrition_model,
        max_output_tokens=300,
    )

    if not result:
        return demo_tip(data)

    return result