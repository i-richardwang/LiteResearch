# backend/literesearch/research_enums.py

from enum import Enum


class ReportType(Enum):
    """Report type enumeration"""

    ResearchReport = "research_report"
    ResourceReport = "resource_report"
    OutlineReport = "outline_report"
    CustomReport = "custom_report"
    DetailedReport = "detailed_report"
    SubtopicReport = "subtopic_report"


class ReportSource(Enum):
    """Report source enumeration"""

    Web = "web"
    Local = "local"
    LangChainDocuments = "langchain_documents"


class Tone(Enum):
    """Report tone enumeration"""

    Objective = "Objective (Present facts and findings fairly and without bias)"
    Formal = "Formal (Follow academic standards with rigorous language and structure)"
    Analytical = "Analytical (Critical evaluation and detailed examination of data and theories)"
    Persuasive = "Persuasive (Aimed at convincing the audience to accept specific viewpoints or arguments)"
    Informative = "Informative (Provide clear and comprehensive information related to the topic)"
    Explanatory = "Explanatory (Clarify complex concepts and processes)"
    Descriptive = "Descriptive (Detailed depiction of phenomena, experiments, or case studies)"
    Critical = "Critical (Evaluate the validity and relevance of research and its conclusions)"
    Comparative = "Comparative (Juxtapose different theories, data, or methods to highlight differences and similarities)"
    Speculative = "Speculative (Explore hypotheses, potential impacts, or future research directions)"
    Reflective = "Reflective (Reflect on the research process and personal insights or experiences)"
    Narrative = "Narrative (Present research findings or methods through storytelling)"
    Humorous = "Humorous (Light-hearted and engaging, making content more understandable and accessible)"
    Optimistic = "Optimistic (Emphasize positive findings and potential benefits)"
    Pessimistic = "Pessimistic (Focus on limitations, challenges, or negative outcomes)"
