from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List
import math

@dataclass
class SimpleRecipe:
    id: int
    title: str
    cuisine: str | None
    tags: list[str]
    prep_minutes: int | None
    cook_minutes: int | None
    cost_cents_est: int | None

@dataclass
class Prefs:
    diet_tags: list[str]
    allergies: list[str]
    disliked: list[str]
    liked: list[str]
    weekly_budget_cents: int | None
    max_prep_min: int | None


#Scoring weights
W_TAG_MATCH = 2.0
W_LIKED = 1.5
W_DISLIKED = -3.0
W_ALLERGY = -10.0
W_CUISINE_MATCH = 0.8
W_TIME = 1.0
W_COST = 1.0

#Soft bounds
def soft_penalty_over(value: int | None, limit: int | None, strength: float = 1) -> float:
    if value is None or limit is None:
        return 0.0
    if value <= limit:
        return 0.0
    #quadratic penalty growth
    diff = value - limit
    return -strength * (diff / (limit + 1e-6)) ** 2

def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(x.lower() for x in a), set(x.lower() for x in b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / max(1, len(sa | sb))


def score_recipe(r: SimpleRecipe, p: Prefs) -> float:
    score = 0.0
    # allergies / dislikes hard penalties
    if any(tok.lower() in {t.lower() for t in r.tags} for tok in p.allergies):
        score += W_ALLERGY
    if any(tok.lower() in {t.lower() for t in r.tags} for tok in p.disliked):
        score += W_DISLIKED

    # positive matches
    score += W_TAG_MATCH * jaccard(r.tags, p.diet_tags)
    score += W_LIKED * jaccard(r.tags, p.liked)
    if p.diet_tags and r.cuisine and r.cuisine.lower() in {t.lower() for t in p.diet_tags}:
        score += W_CUISINE_MATCH

    # time & cost soft constraints
    total_prep = (r.prep_minutes or 0) + (r.cook_minutes or 0)
    score += soft_penalty_over(total_prep, p.max_prep_min, strength=W_TIME)

    # very rough per-recipe cost soft-penalty against fraction of budget
    if p.weekly_budget_cents:
        # assume K dinners/week ~ 7; divisible share
        per_meal_budget = p.weekly_budget_cents / 7.0
        score += soft_penalty_over(r.cost_cents_est or 0, int(per_meal_budget), strength=W_COST)

    return score


def diversify(scored: List[tuple[SimpleRecipe, float]], diversity: float = 0.2, top_k: int = 10) -> List[tuple[SimpleRecipe, float]]:
    # Simple MMR-style diversification using tags
    selected: list[tuple[SimpleRecipe, float]] = []
    remaining = scored.copy()
    while remaining and len(selected) < top_k:
        if not selected:
            best = max(remaining, key=lambda x: x[1])
            selected.append(best)
            remaining.remove(best)
            continue
        # penalize candidates similar to already chosen
        def penalized(s: tuple[SimpleRecipe, float]) -> float:
            r, base = s
            sim = 0.0
            for r_sel, _ in selected:
                sim = max(sim, jaccard(r.tags, r_sel.tags))
            return (1 - diversity) * base - diversity * sim
        best = max(remaining, key=penalized)
        selected.append(best)
        remaining.remove(best)
    return selected


