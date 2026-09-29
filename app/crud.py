from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Plan, User
from .schemas import UserInput


def save_user(
    db: Session,
    data: UserInput,
) -> User:

    existing_user = db.scalar(
        select(User).where(
            User.user_id == data.user_id
        )
    )

    if existing_user:

        existing_user.username = data.username
        existing_user.age = data.age
        existing_user.weight = data.weight
        existing_user.goal = data.goal
        existing_user.intensity = data.intensity

        user = existing_user

    else:

        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    workout_plan: str,
    nutrition_tip: str,
) -> Plan:

    plan = user.plan

    if plan:

        plan.original_plan = workout_plan
        plan.original_nutrition_tip = nutrition_tip

        plan.updated_plan = None
        plan.updated_nutrition_tip = None
        plan.feedback = None
        plan.updated_at = None

    else:

        plan = Plan(
            user_id=user.id,
            original_plan=workout_plan,
            original_nutrition_tip=nutrition_tip,
        )

        db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def update_plan(
    db: Session,
    plan: Plan,
    updated_plan_text: str,
    updated_tip: str,
    feedback: str,
) -> Plan:

    plan.updated_plan = updated_plan_text

    plan.updated_nutrition_tip = updated_tip

    plan.feedback = feedback

    plan.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )


def get_all_users(
    db: Session,
) -> list[User]:

    return list(
        db.scalars(
            select(User).order_by(
                User.created_at.desc()
            )
        ).all()
    )


def delete_user(
    db: Session,
    user_id: str,
) -> bool:

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True