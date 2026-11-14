import logging
import os

from crewai import Agent, Crew, Process, Task

logger = logging.getLogger(__name__)


def _get_search_tool():
    """SerperDevTool اگر کلید موجود باشد.

    بدون کلید Serper از WebsiteSearchTool استفاده می‌شود. این ابزار جست‌وجوی
    وب نیست؛ روی یک وب‌سایت مشخص کار می‌کند و نتیجه‌ی تحقیق محدودتر است.
    """
    if os.getenv("SERPER_API_KEY"):
        from crewai_tools import SerperDevTool

        return SerperDevTool()

    logger.warning(
        "SERPER_API_KEY تنظیم نشده؛ از WebsiteSearchTool استفاده می‌شود "
        "(جست‌وجوی وب نیست و نتایج محدودتر است)."
    )
    from crewai_tools import WebsiteSearchTool

    return WebsiteSearchTool()


def _llm_kwargs() -> dict:
    """اگر MODEL تنظیم شده باشد، مدل را از آن می‌خوانیم؛ وگرنه پیش‌فرض CrewAI."""
    model = os.getenv("MODEL")
    return {"llm": model} if model else {}


def build_crew(use_editor: bool = True) -> Crew:
    search_tool = _get_search_tool()
    llm_kwargs = _llm_kwargs()

    researcher = Agent(
        role="پژوهشگر محتوا",
        goal="جمع‌آوری دقیق‌ترین و به‌روزترین اطلاعات درباره‌ی موضوع داده‌شده",
        backstory="یک تحلیل‌گر باتجربه که در پیدا کردن نکات کلیدی از منابع معتبر مهارت دارد",
        tools=[search_tool],
        verbose=True,
        **llm_kwargs,
    )

    writer = Agent(
        role="نویسنده محتوا",
        goal="نوشتن پست وبلاگ جذاب و روان بر اساس تحقیقات انجام‌شده",
        backstory="نویسنده‌ای حرفه‌ای در حوزه‌ی فناوری و هوش مصنوعی",
        verbose=True,
        **llm_kwargs,
    )

    research_task = Task(
        description=(
            "درباره‌ی {topic} تحقیق کن و ۵ نکته‌ی کلیدی پیدا کن. "
            "برای هر نکته منبع (آدرس یا نام سایت) را ذکر کن. "
            "اگر منبعی را نتوانستی بررسی کنی، آن را به‌صراحت بنویس."
        ),
        expected_output="لیست ۵ نکته‌ی کلیدی به فارسی، هر کدام با ذکر منبع",
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "بر اساس نکات پژوهشگر، یک پست وبلاگ ۳۰۰ تا ۴۰۰ کلمه‌ای به زبان فارسی "
            "درباره‌ی {topic} بنویس. فقط از نکاتی استفاده کن که در خروجی پژوهشگر هستند."
        ),
        expected_output="پست وبلاگ کامل با تیتر، مقدمه، بدنه و نتیجه‌گیری",
        agent=writer,
        context=[research_task],
    )

    agents = [researcher, writer]
    tasks = [research_task, writing_task]

    if use_editor:
        editor = Agent(
            role="ویراستار",
            goal="بازبینی متن از نظر لحن، گرامر و ساختار و تحویل نسخه‌ی نهایی",
            backstory="ویراستاری دقیق با سال‌ها تجربه در ویرایش متون فارسی وب",
            verbose=True,
            **llm_kwargs,
        )
        editing_task = Task(
            description=(
                "پست وبلاگ نویسنده را از نظر لحن، گرامر، املا و ساختار بازبینی و اصلاح کن. "
                "طول متن در بازه‌ی ۳۰۰ تا ۴۰۰ کلمه بماند."
            ),
            expected_output="نسخه‌ی نهایی و اصلاح‌شده‌ی پست وبلاگ",
            agent=editor,
            context=[writing_task],
        )
        agents.append(editor)
        tasks.append(editing_task)

    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )


def generate_post(topic: str, use_editor: bool = True) -> str:
    crew = build_crew(use_editor=use_editor)
    result = crew.kickoff(inputs={"topic": topic})
    return result.raw
