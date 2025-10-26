from pydantic import BaseModel, Field
from typing import List, Optional


class RecipeIn(BaseModel):
    title: str
    cuisine: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    prep_minutes: Optional[int] = None
    cook_minutes: Optional[int] = None
    cost_cents_est: Optional[int] = None
    image_url: Optional[str] = None


class RecipeOut(RecipeIn):
    id: int


class UserPrefs(BaseModel):
    diet_tags: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    disliked: List[str] = Field(default_factory=list)
    liked: List[str] = Field(default_factory=list)
    weekly_budget_cents: Optional[int] = None
    max_prep_min: Optional[int] = None


class RecommendRequest(BaseModel):
    user_id: Optional[int] = None
    prefs: Optional[UserPrefs] = None # allow ad-hoc prefs if no user
    k: int = 10
    diversity: float = 0.2 # 0..1, higher = more variety


class ScoredRecipe(BaseModel):
    recipe: RecipeOut
    score: float