from datetime import datetime, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trivia import Trivia, TriviaStatus, TriviaLevel, Question, QuestionType, TriviaParticipation, UserAnswer
from app.models.user import User
from app.core.config import get_settings

settings = get_settings()


def validate_question_score(base_score: int, time_limit: int) -> tuple[int, int]:
    min_score_for_time = (time_limit * 10) / 0.9
    min_score = max(100, int(min_score_for_time + 99) // 100 * 100)
    if base_score < min_score:
        base_score = min(min_score, 2000)
    if base_score > 2000:
        base_score = 2000
    return base_score, time_limit


def calculate_score(base_score: int, time_limit: int, time_taken_ms: int, is_correct: bool) -> int:
    if not is_correct:
        return 0
    seconds = time_taken_ms / 1000
    if seconds > time_limit:
        return 0
    penalty = int(seconds) * 10
    score = base_score - penalty
    floor = round(base_score * 0.10)
    return max(score, floor)


async def create_trivia(db: AsyncSession, data: dict, user_id: str) -> Trivia:
    trivia = Trivia(
        title=data["title"],
        theme=data.get("theme"),
        level=TriviaLevel(data.get("level", "explorador")),
        unique_code=Trivia.generate_code(),
        start_date=data["start_date"],
        end_date=data["end_date"],
        prize_amount=data.get("prize_amount", 0),
        youtube_episodes=data.get("youtube_episodes"),
        created_by_id=user_id,
        winners_count=data.get("winners_count", 1),
    )
    db.add(trivia)
    await db.commit()
    await db.refresh(trivia)
    return trivia


async def get_trivias(
    db: AsyncSession,
    level: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    admin_user_id: str | None = None,
):
    query = select(Trivia)
    if level:
        query = query.where(Trivia.level == TriviaLevel(level))
    if status:
        query = query.where(Trivia.status == TriviaStatus(status))
    if admin_user_id:
        query = query.where(Trivia.created_by_id == admin_user_id)
    query = query.order_by(desc(Trivia.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_trivia_by_id(db: AsyncSession, trivia_id: str) -> Trivia | None:
    result = await db.execute(select(Trivia).where(Trivia.id == trivia_id))
    return result.scalar_one_or_none()


async def get_trivia_by_code(db: AsyncSession, code: str) -> Trivia | None:
    result = await db.execute(select(Trivia).where(Trivia.unique_code == code.upper()))
    return result.scalar_one_or_none()


async def publish_trivia(db: AsyncSession, trivia_id: str) -> Trivia:
    trivia = await get_trivia_by_id(db, trivia_id)
    if not trivia:
        raise ValueError("Trivia no encontrada")
    trivia.status = TriviaStatus.PUBLISHED
    await db.commit()
    await db.refresh(trivia)
    return trivia


async def add_question(db: AsyncSession, trivia_id: str, data: dict) -> Question:
    trivia = await get_trivia_by_id(db, trivia_id)
    if not trivia:
        raise ValueError("Trivia no encontrada")
    if trivia.status != TriviaStatus.DRAFT:
        raise ValueError("Solo se pueden editar trivias en borrador")

    base_score, time_limit = validate_question_score(
        data.get("base_score", 500), data.get("time_limit", 30)
    )

    count_result = await db.execute(
        select(func.count()).select_from(Question).where(Question.trivia_id == trivia_id)
    )
    count = count_result.scalar() or 0

    question = Question(
        trivia_id=trivia_id,
        question_type=QuestionType(data.get("question_type", "multiple_choice")),
        question_text=data["question_text"],
        options=data["options"],
        base_score=base_score,
        time_limit=time_limit,
        sort_order=count,
        category=data.get("category", "seleccion"),
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def get_questions(db: AsyncSession, trivia_id: str) -> list[Question]:
    result = await db.execute(
        select(Question).where(Question.trivia_id == trivia_id).order_by(Question.sort_order)
    )
    return list(result.scalars().all())


async def start_participation(db: AsyncSession, user_id: str, trivia_code: str) -> TriviaParticipation:
    trivia = await get_trivia_by_code(db, trivia_code)
    if not trivia:
        raise ValueError("Trivia no encontrada")
    if trivia.status not in (TriviaStatus.PUBLISHED, TriviaStatus.ACTIVE):
        raise ValueError("Trivia no disponible")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise ValueError("Usuario no encontrado")

    existing = (await db.execute(
        select(TriviaParticipation).where(
            TriviaParticipation.user_id == user_id,
            TriviaParticipation.trivia_id == trivia.id,
            TriviaParticipation.finished == True,
        )
    )).scalar_one_or_none()
    if existing:
        raise ValueError("Ya participaste en esta trivia")

    participation = TriviaParticipation(
        user_id=user_id,
        trivia_id=trivia.id,
        started_at=datetime.now(timezone.utc),
    )
    db.add(participation)
    await db.commit()
    await db.refresh(participation)
    return participation


async def answer_question(
    db: AsyncSession,
    participation_id: str,
    question_id: str,
    answer_data: dict,
    client_start_ms: int,
    client_end_ms: int,
    server_start: datetime,
) -> UserAnswer:
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if not question:
        raise ValueError("Pregunta no encontrada")

    participation = (await db.execute(
        select(TriviaParticipation).where(TriviaParticipation.id == participation_id)
    )).scalar_one_or_none()
    if not participation or participation.finished:
        raise ValueError("Participacion invalida")

    is_correct = validate_answer(question.question_type, answer_data, question.options)

    server_end = datetime.now(timezone.utc)
    time_taken_ms = int((server_end - server_start).total_seconds() * 1000)

    score = calculate_score(question.base_score, question.time_limit, time_taken_ms, is_correct)

    user_answer = UserAnswer(
        participation_id=participation_id,
        question_id=question_id,
        answer_data=answer_data,
        score=score,
        time_taken_ms=time_taken_ms,
        is_correct=is_correct,
    )
    db.add(user_answer)

    if is_correct:
        participation.correct_count += 1
    elif is_correct is False:
        participation.incorrect_count += 1
    else:
        participation.null_count += 1
    participation.total_score += score

    await db.commit()
    await db.refresh(user_answer)
    return user_answer


async def finish_participation(db: AsyncSession, participation_id: str) -> TriviaParticipation:
    participation = (await db.execute(
        select(TriviaParticipation).where(TriviaParticipation.id == participation_id)
    )).scalar_one_or_none()
    if not participation:
        raise ValueError("Participacion no encontrada")

    participation.finished = True
    participation.completed_at = datetime.now(timezone.utc)

    scores_result = await db.execute(
        select(TriviaParticipation.total_score)
        .where(
            TriviaParticipation.trivia_id == participation.trivia_id,
            TriviaParticipation.finished == True,
        )
        .order_by(desc(TriviaParticipation.total_score))
    )
    all_scores = [s[0] for s in scores_result.all()]
    position = sorted(all_scores, reverse=True).index(participation.total_score) + 1
    participation.position = position

    await db.commit()
    await db.refresh(participation)
    return participation


async def get_participation_result(db: AsyncSession, participation_id: str, user_id: str) -> TriviaParticipation:
    result = await db.execute(
        select(TriviaParticipation).where(
            TriviaParticipation.id == participation_id,
            TriviaParticipation.user_id == user_id,
        )
    )
    participation = result.scalar_one_or_none()
    if not participation:
        raise ValueError("Participacion no encontrada")
    return participation


async def get_trivia_report(db: AsyncSession, trivia_id: str) -> dict:
    trivia = await get_trivia_by_id(db, trivia_id)
    if not trivia:
        raise ValueError("Trivia no encontrada")

    results = await db.execute(
        select(TriviaParticipation, User.email, User.full_name, User.username)
        .join(User, TriviaParticipation.user_id == User.id)
        .where(
            TriviaParticipation.trivia_id == trivia_id,
            TriviaParticipation.finished == True,
        )
        .order_by(desc(TriviaParticipation.total_score))
    )
    rows = results.all()

    participants = []
    for p, email, full_name, username in rows:
        participants.append({
            "user_id": str(p.user_id),
            "email": email,
            "full_name": full_name or username or email,
            "score": p.total_score,
            "correct": p.correct_count,
            "incorrect": p.incorrect_count,
            "null": p.null_count,
            "position": p.position,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        })

    return {
        "trivia_title": trivia.title,
        "trivia_code": trivia.unique_code,
        "level": trivia.level.value,
        "prize": trivia.prize_amount,
        "total_participants": len(participants),
        "participants": participants,
    }


def validate_answer(question_type: QuestionType, answer: dict, options: dict) -> bool | None:
    if question_type in (QuestionType.SURVEY, QuestionType.OPEN_ANSWER):
        return None

    if question_type == QuestionType.MULTIPLE_CHOICE:
        selected = answer.get("selected")
        correct_options = [o for o in options.get("options", []) if o.get("is_correct")]
        return selected == correct_options[0]["id"] if correct_options else False

    return False
