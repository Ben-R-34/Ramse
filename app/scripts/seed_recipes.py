# scripts/seed_recipes.py
import json, os
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal, Base
from app.models import Recipe

Base.metadata.create_all(bind=engine)

path = os.path.join(os.path.dirname(__file__), "..", "seed_recipes.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

with SessionLocal() as db:  # type: Session
    for r in data:
        db.add(Recipe(**r))
    db.commit()
print("Seeded.")