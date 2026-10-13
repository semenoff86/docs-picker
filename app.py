from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from wizard import answer, next_step, rewind, start

app = FastAPI(
    title="Подбор документов для микрозайма",
    description="Принимает ответы и возвращает следующий вопрос или готовый список документов.",
)


class StepIn(BaseModel):
    answers: dict = Field(default_factory=dict)
    question_id: str | None = None
    value: object | None = None


@app.get("/")
def root():
    return start()


@app.post("/step")
def step(payload: StepIn):
    return next_step(payload.answers)


@app.post("/answer")
def do_answer(payload: StepIn):
    if not payload.question_id:
        return {"error": "Нужен question_id"}
    return answer(payload.answers, payload.question_id, payload.value)


@app.post("/rewind")
def do_rewind(payload: StepIn):
    if not payload.question_id:
        return {"error": "Нужен question_id"}
    return rewind(payload.answers, payload.question_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8765, reload=True)
