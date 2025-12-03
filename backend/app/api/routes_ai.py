from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai import (
    Lesson,
    LessonInput,
    Quiz,
    QuizInput,
    QuizQuestion,
    Rubric,
    RubricCriterion,
    RubricInput,
    TextToolInput,
    TextToolResult,
    Worksheet,
    WorksheetInput,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/lesson", response_model=Lesson)
async def generate_lesson(input: LessonInput, current_user: User = Depends(get_current_user)) -> Lesson:
    title = f"Lesson on {input.topic} for grade {input.grade}"
    return Lesson(
        title=title,
        overview=f"An engaging overview of {input.topic} tailored for grade {input.grade}.",
        objectives=input.objectives,
        activities=[
            f"Warm-up discussion about {input.topic}",
            f"Group activity exploring {input.topic}",
            "Exit ticket with reflective question",
        ],
        assessment=f"Short quiz assessing understanding of {input.topic}",
    )


@router.post("/quiz", response_model=Quiz)
async def generate_quiz(input: QuizInput, current_user: User = Depends(get_current_user)) -> Quiz:
    questions = [
        QuizQuestion(
            question=f"What is a key idea in {input.topic} {i+1}?",
            options=["Option A", "Option B", "Option C", "Option D"],
            answer="Option A",
        )
        for i in range(max(1, input.num_questions))
    ]
    return Quiz(topic=input.topic, questions=questions)


@router.post("/worksheet", response_model=Worksheet)
async def generate_worksheet(
    input: WorksheetInput, current_user: User = Depends(get_current_user)
) -> Worksheet:
    activities = [
        f"Define key terms related to {input.topic}",
        f"Match concepts for {input.topic}",
        f"Write a short paragraph about {input.topic} for grade {input.grade}",
    ]
    return Worksheet(topic=input.topic, activities=activities)


@router.post("/rubric", response_model=Rubric)
async def generate_rubric(input: RubricInput, current_user: User = Depends(get_current_user)) -> Rubric:
    criteria = [
        RubricCriterion(criterion="Understanding", description="Shows strong understanding", points=4),
        RubricCriterion(criterion="Application", description="Applies concepts to tasks", points=4),
        RubricCriterion(criterion="Creativity", description="Demonstrates creative thinking", points=4),
    ]
    return Rubric(assignment_type=input.assignment_type, criteria=criteria)


@router.post("/text-tool", response_model=TextToolResult)
async def text_tool(input: TextToolInput, current_user: User = Depends(get_current_user)) -> TextToolResult:
    output = f"[{input.mode}] {input.text}"
    return TextToolResult(output=output)
