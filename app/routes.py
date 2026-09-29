from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import get_settings
from .crud import (
    delete_user,
    get_all_users,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from .database import get_db
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)
from .gemini_generator import (
    generate_workout_gemini,
)
from .schemas import (
    FeedbackRequest,
    UserInput,
)
from .updated_plan import (
    update_workout_plan,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        },
    )


# ---------------------------------------------------------
# GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        # Validate input
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        # Save user
        user = save_user(
            db,
            data,
        )

        # Generate workout
        workout_plan = generate_workout_gemini(
            data
        )

        # Generate nutrition tip
        nutrition_tip = generate_nutrition_tip_with_flash(
            data
        )

        # Save plan
        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "message": None,
                "error": None,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            },
            status_code=400,
        )


# ---------------------------------------------------------
# SUBMIT FEEDBACK
# ---------------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        feedback_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        # Find user
        user = get_user(
            db,
            feedback_data.user_id,
        )

        if not user:

            raise ValueError(
                "User ID was not found."
            )

        if not user.plan:

            raise ValueError(
                "This user does not have a workout plan."
            )

        # Reconstruct profile
        data = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        # Update workout plan
        updated_plan = update_workout_plan(
            data,
            user.plan.original_plan,
            feedback_data.feedback,
        )

        # Generate new tip
        updated_tip = generate_nutrition_tip_with_flash(
            data
        )

        # Save updated plan
        plan = update_plan(
            db,
            user.plan,
            updated_plan,
            updated_tip,
            feedback_data.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "message": "Your workout plan was updated successfully.",
                "error": None,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": None,
                "plan": None,
                "message": None,
                "error": str(exc),
            },
            status_code=400,
        )


# ---------------------------------------------------------
# ADMIN PAGE
# ---------------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    settings = get_settings()

    key = request.query_params.get(
        "key"
    )

    if key != settings.admin_key:

        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "error":
                    "Invalid or missing admin key."
            },
            status_code=401,
        )

    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "admin_key": key,
        },
    )


# ---------------------------------------------------------
# ADMIN DELETE USER
# ---------------------------------------------------------

@router.post(
    "/admin/delete-user"
)
def admin_delete_user(
    request: Request,

    user_id: str = Form(...),

    admin_key: str = Form(...),

    db: Session = Depends(get_db),
):

    settings = get_settings()

    if admin_key != settings.admin_key:

        raise HTTPException(
            status_code=403,
            detail="Invalid admin key.",
        )

    delete_user(
        db,
        user_id,
    )

    return RedirectResponse(
        url=f"/view-all-users?key={admin_key}",
        status_code=303,
    )


# =========================================================
# API ROUTES
# =========================================================


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get(
    "/api/health"
)
def health():

    return {
        "status": "ok",
        "service": "FitBuddy",
    }


# ---------------------------------------------------------
# API GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(
    data: UserInput,
    db: Session = Depends(get_db),
):

    try:

        user = save_user(
            db,
            data,
        )

        workout_plan = generate_workout_gemini(
            data
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            data
        )

        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return {
            "user_id": user.user_id,
            "workout_plan": plan.original_plan,
            "nutrition_tip": plan.original_nutrition_tip,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# API FEEDBACK
# ---------------------------------------------------------

@router.post(
    "/api/submit-feedback"
)
def api_submit_feedback(
    data: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        data.user_id,
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    if not user.plan:

        raise HTTPException(
            status_code=404,
            detail="Workout plan not found.",
        )

    profile = UserInput(
        username=user.username,
        user_id=user.user_id,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )

    try:

        revised_plan = update_workout_plan(
            profile,
            user.plan.original_plan,
            data.feedback,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            profile
        )

        plan = update_plan(
            db,
            user.plan,
            revised_plan,
            nutrition_tip,
            data.feedback,
        )

        return {
            "user_id": user.user_id,
            "updated_plan": plan.updated_plan,
            "nutrition_tip": plan.updated_nutrition_tip,
            "feedback": plan.feedback,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# API LIST USERS
# ---------------------------------------------------------

@router.get(
    "/api/users"
)
def api_users(
    db: Session = Depends(get_db),
):

    users = get_all_users(db)

    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "has_updated_plan":
                bool(
                    user.plan
                    and user.plan.updated_plan
                ),
        }
        for user in users
    ]


# ---------------------------------------------------------
# API DELETE USER
# ---------------------------------------------------------

@router.delete(
    "/api/users/{user_id}"
)
def api_delete_user(
    user_id: str,
    admin_key: str,
    db: Session = Depends(get_db),
):

    settings = get_settings()

    if admin_key != settings.admin_key:

        raise HTTPException(
            status_code=403,
            detail="Invalid admin key.",
        )

    deleted = delete_user(
        db,
        user_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return JSONResponse(
        {
            "message": "User deleted successfully.",
            "user_id": user_id,
        }
    )