import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

from app.crew import generate_post  # noqa: E402

app = FastAPI(title="Blog Content Crew", version="1.0.0")


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, examples=["هوش مصنوعی در بورس تهران"])
    use_editor: bool = True


class GenerateResponse(BaseModel):
    topic: str
    use_editor: bool
    word_count: int
    post: str


class CompareRequest(BaseModel):
    topics: list[str] = Field(..., min_length=2, max_length=5)
    use_editor: bool = True


def _wc(text: str) -> int:
    return len(text.split())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    """تولید یک پست وبلاگ برای یک موضوع."""
    try:
        post = await asyncio.to_thread(generate_post, req.topic, req.use_editor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew failed: {e}")
    return GenerateResponse(
        topic=req.topic, use_editor=req.use_editor, word_count=_wc(post), post=post
    )


@app.post("/compare")
async def compare(req: CompareRequest):
    """اجرای Crew برای چند موضوع و مقایسه‌ی نتایج (الزام تمرین)."""
    try:
        posts = await asyncio.gather(
            *[asyncio.to_thread(generate_post, t, req.use_editor) for t in req.topics]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew failed: {e}")

    results = [
        {"topic": t, "word_count": _wc(p), "post": p}
        for t, p in zip(req.topics, posts)
    ]
    return {
        "use_editor": req.use_editor,
        "summary": [{"topic": r["topic"], "word_count": r["word_count"]} for r in results],
        "results": results,
    }


@app.post("/compare-editor", response_model=dict)
async def compare_editor(req: GenerateRequest):
    """مقایسه‌ی خروجی با ویراستار و بدون ویراستار (برای سوال فکری پایانی)."""
    try:
        without, with_ed = await asyncio.gather(
            asyncio.to_thread(generate_post, req.topic, False),
            asyncio.to_thread(generate_post, req.topic, True),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew failed: {e}")
    return {
        "topic": req.topic,
        "without_editor": {"word_count": _wc(without), "post": without},
        "with_editor": {"word_count": _wc(with_ed), "post": with_ed},
    }
