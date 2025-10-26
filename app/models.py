# app/models.py
from sqlalchemy import Column, Integer, String, Float, ARRAY
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    #diet_tags
    #allergies
    disliked: Mapped[list[str] | None] = mapped_column(PG_ARRAY(String), nullable=True)
    liked: Mapped[list[str] | None] = mapped_column(PG_ARRAY(String), nullable=True)

    weekly_budget_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_prep_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    cuisine: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(PG_ARRAY(String), nullable=True)
    prep_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_cents_est: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(400), nullable=True)

