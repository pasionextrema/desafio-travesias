import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services import trivia_service

router = APIRouter(prefix="/trivias", tags=["trivias"])


@router.get("")
async def list_available_trivias(
    level: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trivias = await trivia_service.get_trivias(db, level=level, status="published", limit=20)
    return [{
        "id": str(t.id),
        "title": t.title,
        "theme": t.theme,
        "level": t.level.value,
        "unique_code": t.unique_code,
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
        "prize_amount": t.prize_amount,
        "winners_count": t.winners_count,
    } for t in trivias]


@router.get("/{code}")
async def get_trivia_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trivia = await trivia_service.get_trivia_by_code(db, code)
    if not trivia:
        raise HTTPException(status_code=404, detail="Trivia no encontrada")
    questions = await trivia_service.get_questions(db, str(trivia.id))
    return {
        "id": str(trivia.id),
        "title": trivia.title,
        "theme": trivia.theme,
        "level": trivia.level.value,
        "unique_code": trivia.unique_code,
        "start_date": trivia.start_date.isoformat(),
        "end_date": trivia.end_date.isoformat(),
        "prize_amount": trivia.prize_amount,
        "winners_count": trivia.winners_count,
        "total_questions": len(questions),
        "total_time": sum(q.time_limit for q in questions),
    }


@router.post("/{code}/start", status_code=201)
async def start_trivia(
    code: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        participation = await trivia_service.start_participation(db, str(user.id), code)
        questions = await trivia_service.get_questions(db, str(participation.trivia_id))
        random.shuffle(questions)

        return {
            "participation_id": str(participation.id),
            "trivia_code": code,
            "started_at": participation.started_at.isoformat(),
            "questions": [{
                "id": str(q.id),
                "question_type": q.question_type.value,
                "question_text": q.question_text,
                "options": q.options,
                "time_limit": q.time_limit,
            } for q in questions],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{code}/answer")
async def answer_trivia_question(
    code: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    server_now = datetime.now(timezone.utc)
    try:
        answer = await trivia_service.answer_question(
            db,
            participation_id=data["participation_id"],
            question_id=data["question_id"],
            answer_data=data.get("answer_data", {}),
            client_start_ms=data.get("client_start_ms", 0),
            client_end_ms=data.get("client_end_ms", 0),
            server_start=server_now,
        )
        return {
            "is_correct": answer.is_correct,
            "score": answer.score,
            "time_taken_ms": answer.time_taken_ms,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{code}/finish")
async def finish_trivia(
    code: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        participation = await trivia_service.finish_participation(db, data["participation_id"])
        return {
            "participation_id": str(participation.id),
            "total_score": participation.total_score,
            "correct_count": participation.correct_count,
            "incorrect_count": participation.incorrect_count,
            "null_count": participation.null_count,
            "position": participation.position,
            "finished": participation.finished,
            "completed_at": participation.completed_at.isoformat() if participation.completed_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
