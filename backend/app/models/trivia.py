import enum
import secrets
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Boolean, Enum, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class TriviaLevel(str, enum.Enum):
    EXPLORADOR = "explorador"
    NAVEGANTE = "navegante"
    CONSTRUCTOR = "constructor"
    ESTRELLA = "estrella"


class TriviaStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    FINISHED = "finished"


class Trivia(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trivias"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    theme: Mapped[str | None] = mapped_column(String(200), nullable=True)
    level: Mapped[TriviaLevel] = mapped_column(Enum(TriviaLevel), default=TriviaLevel.EXPLORADOR, nullable=False)
    unique_code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    prize_amount: Mapped[int] = mapped_column(Integer, default=0)
    youtube_episodes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[TriviaStatus] = mapped_column(Enum(TriviaStatus), default=TriviaStatus.DRAFT, nullable=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    winners_count: Mapped[int] = mapped_column(Integer, default=1)

    questions: Mapped[list["Question"]] = relationship("Question", back_populates="trivia", cascade="all, delete-orphan", order_by="Question.sort_order")
    participations: Mapped[list["TriviaParticipation"]] = relationship("TriviaParticipation", back_populates="trivia", cascade="all, delete-orphan")

    @staticmethod
    def generate_code() -> str:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        while True:
            code = "".join(secrets.choice(alphabet) for _ in range(6))
            return code


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTI_SELECT = "multi_select"
    TRUE_FALSE = "true_false"
    FILL_BLANKS = "fill_blanks"
    DRAG_DROP = "drag_drop"
    DROPDOWN = "dropdown"
    CATEGORIZE = "categorize"
    REORDER = "reorder"
    MATCH = "match"
    TEXT_HIGHLIGHT = "text_highlight"
    IMAGE_LABEL = "image_label"
    HOTSPOT = "hotspot"
    AUDIO = "audio"
    VIDEO = "video"
    CASE_ANALYSIS = "case_analysis"
    FIND_ERROR = "find_error"
    PROGRESSIVE_IMAGE = "progressive_image"
    SURVEY = "survey"
    OPEN_ANSWER = "open_answer"


class Question(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "questions"

    trivia_id: Mapped[str] = mapped_column(ForeignKey("trivias.id", ondelete="CASCADE"), nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    question_text: Mapped[dict] = mapped_column(JSONB, nullable=False)
    options: Mapped[dict] = mapped_column(JSONB, nullable=False)
    base_score: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[str] = mapped_column(String(50), default="seleccion")
    status: Mapped[str] = mapped_column(String(20), default="approved")

    trivia: Mapped["Trivia"] = relationship("Trivia", back_populates="questions")


class TriviaParticipation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trivia_participations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trivia_id: Mapped[str] = mapped_column(ForeignKey("trivias.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    trivia: Mapped["Trivia"] = relationship("Trivia", back_populates="participations")
    answers: Mapped[list["UserAnswer"]] = relationship("UserAnswer", back_populates="participation", cascade="all, delete-orphan")


class UserAnswer(UUIDMixin, Base):
    __tablename__ = "user_answers"

    participation_id: Mapped[str] = mapped_column(ForeignKey("trivia_participations.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    time_taken_ms: Mapped[int] = mapped_column(Integer, default=0)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    participation: Mapped["TriviaParticipation"] = relationship("TriviaParticipation", back_populates="answers")
