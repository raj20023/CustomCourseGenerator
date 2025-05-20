from typing import List, Dict, Any
from pydantic import BaseModel, Field


class Task(BaseModel):
    module_1: str = Field(description="Module Title")
    description_1: str = Field(description="Module description")
    learning_objectives_1: str = Field(description='["objective 1", "objective 2", "objective 3"]')
    module_2: str = Field(description="Module Title")
    description_2: str = Field(description="Module description")
    learning_objectives_2: str = Field(description='["objective 1", "objective 2", "objective 3"]')
    module_3: str = Field(description="Module Title")
    description_3: str = Field(description="Module description")
    learning_objectives_3: str = Field(description='["objective 1", "objective 2", "objective 3"]')

class Section(BaseModel):
    title: str = Field(description="Title of the section")
    content: str = Field(description="Detailed content of the section (min 300-500 words per section)")
    subsections: List[Dict[str, str]] = Field(description="List of 2-4 subsections with titles and content (200+ words each)")

class Example(BaseModel):
    title: str = Field(description="Title of the example")
    scenario: str = Field(description="Background and context for the example")
    content: str = Field(description="Detailed step-by-step walkthrough with explanations (300+ words)")
    key_takeaways: List[str] = Field(description="List of key takeaways from this example")

class ModuleContent(BaseModel):
    title: str = Field(description="Module title")
    introduction: str = Field(description="Comprehensive introduction (300+ words)")
    sections: List[Section] = Field(description="List of 4-7 detailed sections with subsections")
    key_concepts: List[str] = Field(description="List of 8-12 key concepts covered in the module")
    examples: List[Example] = Field(description="List of 3-5 detailed examples with scenarios and takeaways")
    practice_activities: List[Dict[str, str]] = Field(description="List of 3-5 practice activities with instructions")
    summary: str = Field(description="Comprehensive summary (250+ words)")
    further_reading: List[Dict[str, str]] = Field(description="List of suggested resources for deeper learning")

class DetailedQuizQuestion(BaseModel):
    question: str = Field(description="Detailed question text (at least 50 words)")
    context: str = Field(description="Background information and context for the question (100+ words)")
    options: List[str] = Field(description="Detailed multiple choice options (each 20+ words)")
    correct_answer: str = Field(description="The correct option")
    explanation: str = Field(description="Detailed explanation of why this answer is correct (150+ words)")

class DetailedPracticeProblem(BaseModel):
    problem: str = Field(description="Comprehensive problem description (200+ words)")
    context: str = Field(description="Background and real-world context (100+ words)")
    solution: str = Field(description="Step-by-step detailed solution with explanations (300+ words)")
    hints: List[str] = Field(description="Progressive hints to help students solve the problem")
    learning_points: List[str] = Field(description="Key learning points from this problem")

class DetailedProjectIdea(BaseModel):
    title: str = Field(description="Project title")
    description: str = Field(description="Comprehensive project description (300+ words)")
    learning_goals: List[str] = Field(description="Specific learning goals this project addresses")
    steps: List[Dict[str, str]] = Field(description="Detailed step-by-step implementation guide")
    resources_needed: List[str] = Field(description="Resources needed to complete the project")
    evaluation_criteria: List[str] = Field(description="Criteria for evaluating project success")
    extensions: List[str] = Field(description="Ways to extend or enhance the project")

class DetailedModuleAssessment(BaseModel):
    module_title: str = Field(description="Module title")
    quiz_questions: List[DetailedQuizQuestion] = Field(description="List of 8-12 detailed quiz questions with explanations")
    practice_problems: List[DetailedPracticeProblem] = Field(description="List of 4-6 comprehensive practice problems")
    project_ideas: List[DetailedProjectIdea] = Field(description="List of 3-5 detailed project proposals")
    self_assessment: List[Dict[str, str]] = Field(description="List of reflection questions with guidelines")
    grading_rubrics: List[Dict[str, Any]] = Field(description="Detailed grading rubrics for assignments")

class DetailedReading(BaseModel):
    title: str = Field(description="Reading title")
    author: str = Field(description="Author name(s)")
    description: str = Field(description="Detailed description of the reading (150+ words)")
    key_topics: List[str] = Field(description="Key topics covered in this reading")
    relevance: str = Field(description="Explanation of relevance to the module (100+ words)")
    difficulty: str = Field(description="Reading difficulty and estimated time commitment")
    discussion_questions: List[str] = Field(description="Questions to consider while reading")

class DetailedAdvancedTopic(BaseModel):
    title: str = Field(description="Topic title")
    description: str = Field(description="Comprehensive description of the topic (250+ words)")
    prerequisites: List[str] = Field(description="Knowledge prerequisites for understanding this topic")
    learning_pathway: str = Field(description="Suggested approach to learning this topic (150+ words)")
    resources: List[Dict[str, str]] = Field(description="Specific resources for learning this topic")
    applications: List[str] = Field(description="Real-world applications of this topic")

class DetailedToolResource(BaseModel):
    name: str = Field(description="Tool name")
    type: str = Field(description="Type of tool (software, framework, methodology, etc.)")
    description: str = Field(description="Detailed description of the tool (200+ words)")
    use_cases: List[str] = Field(description="Specific use cases relevant to the module")
    getting_started: str = Field(description="Detailed guide for getting started (150+ words)")
    alternatives: List[Dict[str, str]] = Field(description="Alternative tools with comparisons")

class DetailedGlossaryItem(BaseModel):
    term: str = Field(description="Term")
    definition: str = Field(description="Comprehensive definition (50+ words)")
    context: str = Field(description="Usage context and importance (75+ words)")
    examples: List[str] = Field(description="Examples of the term in use")
    related_terms: List[str] = Field(description="Related terms to explore")

class DetailedCaseStudy(BaseModel):
    title: str = Field(description="Case study title")
    scenario: str = Field(description="Detailed real-world scenario (300+ words)")
    analysis: str = Field(description="In-depth analysis of the case (400+ words)")
    lessons: List[str] = Field(description="Key lessons from this case study")
    questions: List[str] = Field(description="Discussion questions based on this case")

class DetailedModuleResources(BaseModel):
    module_title: str = Field(description="Module title")
    recommended_readings: List[DetailedReading] = Field(description="List of 5-8 detailed reading recommendations")
    advanced_topics: List[DetailedAdvancedTopic] = Field(description="List of 4-6 advanced topics with learning pathways")
    tools_and_resources: List[DetailedToolResource] = Field(description="List of 4-6 detailed tool/resource descriptions")
    glossary: List[DetailedGlossaryItem] = Field(description="List of 10-15 detailed glossary items")
    case_studies: List[DetailedCaseStudy] = Field(description="List of 2-4 detailed case studies")
    cheat_sheets: List[Dict[str, Any]] = Field(description="Quick reference materials for key concepts")

class Module(BaseModel):
    title: str = Field(description="Module title")
    description: str = Field(description="Module description")

class CourseMetadata(BaseModel):
    title: str = Field(description="Course title")
    description: str = Field(description="Comprehensive course description")
    target_audience: str = Field(description="Description of the intended audience")
    prerequisites: List[str] = Field(description="List of prerequisites for the course")
    learning_outcomes: List[str] = Field(description="List of learning outcomes")
    modules: List[Module] = Field(description="List of modules with titles and descriptions")
    estimated_duration: str = Field(description="Estimated completion time")
    difficulty_level: str = Field(description="Course difficulty")
    instructional_approach: str = Field(description="Description of teaching approach")
    authors_note: str = Field(description="Note from the course creators")