# backend/literesearch/research_prompts.py

from datetime import date, datetime, timezone
from backend.literesearch.research_enums import ReportSource, Tone


def auto_agent_instructions():
    return """
    This task involves researching a given topic, regardless of its complexity or whether there are clear answers. Research is performed by specific agents, and each agent requires different instructions based on their type and role definition.

    Intelligent Agents
    Agents are determined based on the topic's domain and specific agent names available for researching the provided topic. Intelligent agents are categorized by their professional domains, with each agent type associated with corresponding emojis.

    Examples:
    Task: "Should I invest in Apple stock?"
    Response:
    {
        "server": "💰 Financial Analyst",
        "agent_role_prompt": "You are an experienced AI financial analyst assistant. Your primary goal is to write comprehensive, insightful, objective, and well-structured financial reports based on provided data and trends."
    }
    Task: "Could sneaker reselling become a profitable business?"
    Response:
    {
        "server": "📈 Business Analyst",
        "agent_role_prompt": "You are an experienced AI business analyst assistant. Your primary goal is to create comprehensive, insightful, objective, and systematic business reports based on provided business data, market trends, and strategic analysis."
    }
    Task: "What are the most interesting attractions in Tel Aviv?"
    Response:
    {
        "server": "🌍 Travel Advisor",
        "agent_role_prompt": "You are a knowledgeable AI travel advisor assistant. Your primary task is to write engaging, insightful, objective, and well-structured travel reports for specified locations, including historical, attraction, and cultural insights."
    }
    """


def generate_search_queries_prompt(
    question, parent_query, report_type, max_iterations=5
):
    if report_type == "detailed_report" or report_type == "subtopic_report":
        task = f"{parent_query} - {question}"
    else:
        task = question

    return (
        f'Please generate {max_iterations} Google search queries for online searching to form an objective opinion on the following task: "{task}"\n'
        f'You must respond with a list of strings in the following format: ["query1", "query2", "query3"].\n'
        f"The response should only contain the list."
    )


def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
):
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
            You must list all used source URLs as references at the end of the report, ensuring no duplicate sources are added, with each source listed only once.
            Each URL should be in hyperlink format: [Website Name](URL)
            Additionally, you must include hyperlinks when citing relevant URLs in the report:

            Example: Author, A. A. (Year, Month Day). Web Page Title. Website Name. [Website Name](URL)
            """
    else:
        reference_prompt = f"""
            You must list all used source document names as references at the end of the report, ensuring no duplicate sources are added, with each source listed only once.
        """

    tone_prompt = f"Please write the report in a {tone.value} tone." if tone else ""

    return f"""
Information: "{context}"
---
Using the above information, answer the following query or task in the form of a detailed report: "{question}" --
The report should focus on answering the query, be well-structured, informative, in-depth and comprehensive, including facts and data (if available), with at least {total_words} words.
You should use all relevant and necessary information as thoroughly as possible to write the report.

Please follow all the following guidelines in your report:
- You must form your own specific and valid viewpoints based on the given information. Do not draw generic and meaningless conclusions.
- You must write the report using markdown syntax and {report_format} format.
- Use an objective and impartial journalistic tone.
- Use {report_format} format in-text citations and place them as markdown hyperlinks at the end of sentences or paragraphs that cite them, such as: ([In-text citation](url)).
- Don't forget to add a reference list in {report_format} format at the end of the report, including complete URL links (without hyperlinks).
- {reference_prompt}
- {tone_prompt}
- You must write the entire report in English.

Please do your best, this is very important for my career.
Assume the current date is {date.today()}.
"""


def generate_resource_report_prompt(
    question, context, report_source, report_format="apa", total_words=1000
):
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = "You must include all relevant source URLs."
    else:
        reference_prompt = "You must list all used source document names as references at the end of the report, ensuring no duplicate sources are added, with each source listed only once."

    return f"""
"{context}"

Based on the above information, generate a literature recommendation report for the following question or topic: "{question}". The report should analyze each recommended resource in detail, explaining how each source helps answer the research question.
Focus on the relevance, reliability, and importance of each source.
Ensure the report is well-structured, informative, in-depth and detailed, following Markdown syntax.
Include relevant facts, data, and numbers where possible.
The report should be at least {total_words} words.
{reference_prompt}
You must write the entire report in English.
    """


def generate_outline_report_prompt(
    question, context, report_source, report_format="apa", total_words=1000
):
    return f"""
"{context}"

Using the above information, generate a research report outline (using Markdown syntax) for the following question or topic: "{question}". The outline should provide a well-structured framework for the research report, including main sections, subsections, and key points to be covered.
The research report should be detailed, informative, and in-depth, with at least {total_words} words.
Use appropriate Markdown syntax to format the outline, ensuring readability.
You must write the entire outline in English.
    """


def generate_subtopic_report_prompt(
    current_subtopic,
    existing_headers: list,
    main_topic: str,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800,
    tone: Tone = Tone.Objective,
) -> str:
    return f"""
"Background Information":
"{context}"

"Topic and Subtopic":
Using the latest available information, write a detailed report on the subtopic "{current_subtopic}" under the main topic "{main_topic}".
The number of subsections should not exceed {max_subsections}.

"Content Focus":
- The report should focus on answering the question, be well-structured, informative, in-depth and comprehensive, including facts and data (if available).
- Use markdown syntax, following {report_format.upper()} format.

"Structure and Format":
- Since this subtopic report will be part of a larger report, only include the main content divided into appropriate subtopics, without introduction or conclusion sections.

- You must include markdown hyperlinks when citing relevant URLs in the report, for example:

    This is sample text. ([Website Name](URL))

"Existing Subtopic Reports":
- The following is a list of existing subtopic reports and their section titles:

    {existing_headers}.

- Do not use any of the above titles or related details to avoid duplication. Use smaller Markdown headings (such as H2 or H3) to organize content structure, avoiding the largest heading (H1) as it will be used for the larger report title.

"Date":
If needed, assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')}.

"Important Notes!":
- Must focus on the topic! Must omit any information unrelated to it!
- Must not include any introduction, conclusion, summary, or reference sections.
- You must use markdown hyperlinks ([Website Name](URL)) where necessary.
- The report should be at least {total_words} words.
- Use a {tone.value} tone throughout the report.
- You must write the entire report in English.
"""


def generate_report_introduction_prompt(
    question: str, research_summary: str = ""
) -> str:
    return f"""{research_summary}\n
    Using the above latest information, prepare a detailed report introduction for the topic -- {question}.
    - The introduction should be concise, well-structured, informative, and use markdown syntax.
    - Since this introduction will be part of a larger report, do not include any other sections that would normally exist in a report.
    - The introduction should be preceded by an H1 title suitable for the entire report.
    - You must use markdown hyperlinks ([Website Name](URL)) where necessary.
    - You must write the entire introduction in English.
    If needed, assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')}.
"""


def get_report_by_type(report_type: str):
    report_type_mapping = {
        "research_report": generate_report_prompt,
        "resource_report": generate_resource_report_prompt,
        "outline_report": generate_outline_report_prompt,
        "subtopic_report": generate_subtopic_report_prompt,
    }
    return report_type_mapping.get(report_type, generate_report_prompt)


def generate_subtopics_prompt() -> str:
    return """
    Based on the following topic:

    {task}

    and research data:

    {data}

    - Build a list of subtopics that will become the headings of the report document to be generated.
    - The following is a list of possible subtopics: {subtopics}.
    - There should be no duplicate subtopics.
    - The number of subtopics should not exceed {max_subtopics}.
    - Finally, sort the subtopics by task so that they are relevant and meaningful when presented in the detailed report.

    "Important Notes!":
    - Each subtopic must be relevant to the topic and the provided research data!
    - You must write all subtopics in English.
"""
