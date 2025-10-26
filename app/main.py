# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .db import Base, engine, get_db
from .models import User, Recipe
from .schemas import RecipeIn, RecipeOut, RecommendRequest, ScoredRecipe, UserPrefs
from .recommender import SimpleRecipe, Prefs, score_recipe, diversify

app = FastAPI(title="Meal Planner Recommender", version="1.0")

# Create tables on startup (dev only)
Base.metadata.create_all(bind=engine)

@app.get("/recipes", response_model=List[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    rows = db.query(Recipe).all()
    return [RecipeOut(
        id=r.id, title=r.title, cuisine=r.cuisine, tags=r.tags or [],
        prep_minutes=r.prep_minutes, cook_minutes=r.cook_minutes,
        cost_cents_est=r.cost_cents_est, image_url=r.image_url
    ) for r in rows]

@app.post("/recipes", response_model=RecipeOut)
def create_recipe(payload: RecipeIn, db: Session = Depends(get_db)):
    r = Recipe(
        title=payload.title,
        cuisine=payload.cuisine,
        tags=payload.tags,
        prep_minutes=payload.prep_minutes,
        cook_minutes=payload.cook_minutes,
        cost_cents_est=payload.cost_cents_est,
        image_url=payload.image_url,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return RecipeOut(id=r.id, **payload.model_dump())

@app.post("/recommend", response_model=List[ScoredRecipe])
def recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    # Load user prefs or use ad-hoc prefs
    if req.user_id:
        u = db.query(User).filter(User.id == req.user_id).first()
        if not u:
            raise HTTPException(404, "User not found")
        prefs = UserPrefs(
            diet_tags=u.diet_tags or [],
            allergies=u.allergies or [],
            disliked=u.disliked or [],
            liked=u.liked or [],
            weekly_budget_cents=u.weekly_budget_cents,
            max_prep_min=u.max_prep_min,
        )
    else:
        if not req.prefs:
            prefs = UserPrefs()
        else:
            prefs = req.prefs

    P = Prefs(
        diet_tags=prefs.diet_tags,
        allergies=prefs.allergies,
        disliked=prefs.disliked,
        liked=prefs.liked,
        weekly_budget_cents=prefs.weekly_budget_cents,
        max_prep_min=prefs.max_prep_min,
    )

    recipes = db.query(Recipe).all()
    pool = [SimpleRecipe(
        id=r.id, title=r.title, cuisine=r.cuisine,
        tags=r.tags or [], prep_minutes=r.prep_minutes,
        cook_minutes=r.cook_minutes, cost_cents_est=r.cost_cents_est
    ) for r in recipes]

    scored = [(r, score_recipe(r, P)) for r in pool]
    scored.sort(key=lambda x: x[1], reverse=True)

    diversified = diversify(scored, diversity=req.diversity, top_k=req.k)

    # shape response
    out: List[ScoredRecipe] = []
    for r, s in diversified:
        row = next(rr for rr in recipes if rr.id == r.id)
        out.append(ScoredRecipe(
            recipe=RecipeOut(
                id=row.id, title=row.title, cuisine=row.cuisine, tags=row.tags or [],
                prep_minutes=row.prep_minutes, cook_minutes=row.cook_minutes,
                cost_cents_est=row.cost_cents_est, image_url=row.image_url
            ),
            score=float(round(s, 4))
        ))
    return out