from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.trivia import Trivia, TriviaStatus, Question
from app.services import trivia_service
from app.services.user_service import get_user_profile

router = APIRouter(prefix="/admin/trivias", tags=["admin-trivias"])


def require_admin_or_colab(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.ADMIN, UserRole.COLABORADOR):
        raise HTTPException(status_code=403, detail="Requiere rol admin o colaborador")
    return user


@router.post("", status_code=201)
async def create_trivia(
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    try:
        trivia = await trivia_service.create_trivia(db, data, str(user.id))
        return {
            "id": str(trivia.id),
            "title": trivia.title,
            "level": trivia.level.value,
            "unique_code": trivia.unique_code,
            "status": trivia.status.value,
            "prize_amount": trivia.prize_amount,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_trivias(
    level: str | None = None,
    status: str | None = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    trivias = await trivia_service.get_trivias(
        db, level=level, status=status, limit=limit, offset=offset,
        admin_user_id=str(user.id) if user.role == UserRole.COLABORADOR else None,
    )
    return [{
        "id": str(t.id),
        "title": t.title,
        "theme": t.theme,
        "level": t.level.value,
        "unique_code": t.unique_code,
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
        "prize_amount": t.prize_amount,
        "status": t.status.value,
        "winners_count": t.winners_count,
        "created_at": t.created_at.isoformat(),
    } for t in trivias]


@router.get("/{trivia_id}")
async def get_trivia_detail(
    trivia_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    trivia = await trivia_service.get_trivia_by_id(db, trivia_id)
    if not trivia:
        raise HTTPException(status_code=404, detail="Trivia no encontrada")
    questions = await trivia_service.get_questions(db, trivia_id)
    return {
        "id": str(trivia.id),
        "title": trivia.title,
        "theme": trivia.theme,
        "level": trivia.level.value,
        "unique_code": trivia.unique_code,
        "start_date": trivia.start_date.isoformat(),
        "end_date": trivia.end_date.isoformat(),
        "prize_amount": trivia.prize_amount,
        "status": trivia.status.value,
        "winners_count": trivia.winners_count,
        "youtube_episodes": trivia.youtube_episodes,
        "created_at": trivia.created_at.isoformat(),
        "questions": [{
            "id": str(q.id),
            "question_type": q.question_type.value,
            "question_text": q.question_text,
            "options": q.options,
            "base_score": q.base_score,
            "time_limit": q.time_limit,
            "sort_order": q.sort_order,
            "category": q.category,
        } for q in questions],
    }


@router.put("/{trivia_id}")
async def update_trivia(
    trivia_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    trivia = await trivia_service.get_trivia_by_id(db, trivia_id)
    if not trivia:
        raise HTTPException(status_code=404, detail="Trivia no encontrada")
    if trivia.status != TriviaStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Solo se pueden editar trivias en borrador")
    for key in ("title", "theme", "level", "start_date", "end_date", "prize_amount", "winners_count", "youtube_episodes"):
        if key in data:
            setattr(trivia, key, data[key])
    await db.commit()
    return {"message": "Trivia actualizada"}


@router.post("/{trivia_id}/publish")
async def publish_trivia(
    trivia_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    try:
        trivia = await trivia_service.publish_trivia(db, trivia_id)
        return {"message": "Trivia publicada", "status": trivia.status.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{trivia_id}/questions", status_code=201)
async def add_question(
    trivia_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    try:
        question = await trivia_service.add_question(db, trivia_id, data)
        return {
            "id": str(question.id),
            "question_type": question.question_type.value,
            "base_score": question.base_score,
            "time_limit": question.time_limit,
            "sort_order": question.sort_order,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/questions/{question_id}")
async def update_question(
    question_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    for key in ("question_text", "options", "base_score", "time_limit", "sort_order", "category"):
        if key in data:
            setattr(question, key, data[key])
    if "base_score" in data or "time_limit" in data:
        question.base_score, question.time_limit = trivia_service.validate_question_score(
            question.base_score, question.time_limit
        )
    await db.commit()
    return {"message": "Pregunta actualizada"}


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    await db.delete(question)
    await db.commit()
    return {"message": "Pregunta eliminada"}


@router.get("/{trivia_id}/report")
async def get_report(
    trivia_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin_or_colab),
):
    try:
        return await trivia_service.get_trivia_report(db, trivia_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
