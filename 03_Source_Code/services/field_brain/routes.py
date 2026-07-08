"""Field Brain routes — /api/v1/services/field-brain"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from pydantic import BaseModel
from field_brain_svc import FieldBrainService

router = APIRouter()


class FieldBrainQuery(BaseModel):
    question: str


@router.get("")
def service_info():
    return FieldBrainService.info()


@router.post("/ask")
def ask(req: FieldBrainQuery):
    return FieldBrainService.query(req.question)
