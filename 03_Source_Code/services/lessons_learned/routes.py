"""Lessons Learned routes — /api/v1/services/lessons-learned"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query
from typing import Optional
from pydantic import BaseModel
from lessons_learned_svc import LessonsLearnedService

router = APIRouter()

class LessonCreate(BaseModel):
    title: str
    description: str
    category: str = "other"
    csi_division: Optional[str] = None
    project_id: Optional[int] = None
    outcome: str = ""
    future_recommendation: str = ""

@router.get("")
def service_info():
    return LessonsLearnedService.info()

@router.get("/lessons")
def list_lessons(category: Optional[str] = None, csi_division: Optional[str] = None):
    return LessonsLearnedService.list_lessons(category, csi_division)

@router.get("/search")
def search_lessons(q: str):
    return LessonsLearnedService.search_lessons(q)

@router.post("/lessons")
def add_lesson(req: LessonCreate):
    return LessonsLearnedService.add_lesson(
        req.title, req.description, req.category,
        req.csi_division, req.project_id, req.outcome, req.future_recommendation
    )
