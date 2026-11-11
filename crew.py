import os

from crewai import Agent, Crew, Process, Task


def _get_search_tool():
    """SerperDevTool اگر کلید موجود باشد، وگرنه WebsiteSearchTool."""
    if os.getenv("SERPER_API_KEY"):
        from crewai_tools import SerperDevTool

        return SerperDevTool()
    from crewai_tools import WebsiteSearchTool

    return WebsiteSearchTool()


def build_crew(use_editor: bool = True) -> Crew:
    search_tool = _get_search_tool()

    researcher = Agent(
        role="پژوهشگر محتوا",
        goal="جمع‌آوری دقیق‌ترین و به‌روزترین اطلاعات درباره‌ی موضوع داده‌شده",
        backstory="یک تحلیل‌گر باتجربه که در پیدا کردن نکات کلیدی از منابع معتبر مهارت دارد",
        tools=[search_tool],
        verbose=True,
    )

    writer = Agent(
        role="نویسنده محتوا",
        goal="نوشتن پست وبلاگ جذاب و روان بر اساس تحقیقات انجام‌شده",
        backstory="نویسنده‌ای حرفه‌ای در حوزه‌ی فناوری و هوش مصنوعی",
        verbose=True,
    )

    research_task = Task(
        description=(
            "درباره‌ی {topic} تحقیق کن و ۵ نکته‌ی کلیدی پیدا کن. "
            "برای هر نکته منبع (آدرس یا نام سایت) را ذکر کن."
        ),
        expected_output="لیست ۵ نکته‌ی کلیدی به فارسی، هر کدام با ذکر منبع",
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "بر اساس نکات پژوهشگر، یک پست وبلاگ ۳۰۰ تا ۴۰۰ کلمه‌ای به زبان فارسی "
            "درباره‌ی {topic} بنویس."
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
