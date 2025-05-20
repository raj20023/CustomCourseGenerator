import streamlit as st
import json
import time
import uuid
import pandas as pd
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

# Create folders for storing courses
os.makedirs("courses", exist_ok=True)

# Set page config
st.set_page_config(
    page_title="Advanced Course Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "jobs" not in st.session_state:
    st.session_state.jobs = {}

if "current_job_id" not in st.session_state:
    st.session_state.current_job_id = None

if "course_data" not in st.session_state:
    st.session_state.course_data = {}

# Initialize model
@st.cache_resource
def get_model():
    # You can swap this with OpenAI if you prefer
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model="gpt-4o")

# Main title
st.title("📚 Advanced Course Generator")
st.markdown("Generate professional-quality courses with AI and enhance them with web search.")

# Add tabs for navigation
tab1, tab2, tab3 = st.tabs(["Create Course", "My Courses", "About"])

# Helper functions
def parse_json(text):
    """Helper function to extract and parse JSON from text"""
    try:
        # First try direct JSON parsing
        return json.loads(text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON using regex
        text = text.replace("```json", "").replace("```", "")
        try:
            # Try various approaches to fix and parse the JSON
            import re
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                raise ValueError("Could not find JSON in response")
        except Exception:
            # Last resort: use the json formater bot
            return json_maker_bot(text)

def json_maker_bot(json_text):
    """Fix malformed JSON using the model"""
    model = get_model()
    print("Json bot triggred...")
    json_formator_template = """
    You are an expert json issue resolver, you can make all json in proper format.

    Here is the json which dosen't have proper format of the json, Please make it in proper json format.
    {json_text}

    Strict Instructions:
    - return only corrected json format only.
    - don't give any other text then corrected json response.
    - *json needs to be 100 percent correct in the output.*
    """
    json_formator_prompt = ChatPromptTemplate.from_template(json_formator_template)
    formatted_prompt = json_formator_prompt.format_messages(json_text=json_text)
    model_response = model.invoke(formatted_prompt)
    
    cleaned_response = model_response.content.replace("```json", "").replace("```", "").strip()
    
    # Try to parse the cleaned response
    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        # If still not valid JSON, try a more aggressive approach
        import ast
        try:
            # Use ast.literal_eval to safely evaluate the string
            return ast.literal_eval(cleaned_response)
        except:
            # If all else fails, return an empty dict
            return {}

async def perform_web_search(query, num_results=5):
    """Perform web search using Serper API"""    
    try:
        client = TavilyClient(os.getenv("TAVILY_API_KEY"))
        response = client.search(
            query=query,
            max_results=num_results
        )
        return response
    except Exception as e:
        st.error(f"Error during search: {str(e)}")
        return {"error": str(e), "results": []}
        
async def fetch_webpage_content(url):
    """Fetch content from a webpage"""
    try:
        client = TavilyClient(os.getenv("TAVILY_API_KEY"))
        response = client.extract(
            urls=[url],
            extract_depth="advanced"
        )
        return response["results"]
    except Exception as e:
        st.warning(f"Error fetching {url}: {e}")
        return ""

def save_course_to_file(job_id, course_data):
    """Save the course data to a JSON file"""
    filename = f"courses/course_{job_id}.json"
    with open(filename, "w") as f:
        json.dump(course_data, f, indent=2)
    return filename

def load_course_from_file(filename):
    """Load course data from a JSON file"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading course data: {str(e)}")
        return {}

# ---------------- Course Generation Functions ----------------

async def web_search_enhancer(course_topic):
    """Enhance course content using web search"""
    with st.spinner("Enhancing with web search..."):
        print("started")
        search_query = f"best practices teaching {course_topic} curriculum"
        
        # Perform web search
        search_results = await perform_web_search(search_query)
        # Extract useful information from search results
        enhanced_content = {
            "search_query": search_query,
            "results": search_results.get("results", [])[:5],
            "extracted_insights": []
        }
        
        # Try to fetch content from top results
        if "results" in search_results:
            progress_bar = st.progress(0)
            for i, result in enumerate(search_results["results"][:5]):
                if "url" in result:
                    progress_bar.progress((i+1)/5)
                    st.write(f"Analyzing: {result.get('title', 'Source')}")
                    
                    content = await fetch_webpage_content(result["url"])
                    # Extract insights from the content
                    insights_prompt = """
                    Extract 3-5 key educational insights from this content that would be valuable for 
                    creating a course on {topic}. Focus on teaching methodologies, important concepts,
                    and best practices. Return the insights as a JSON array of strings.
                    
                    Content: {content}
                    
                    Strictly Return ONLY a JSON array like ["insight 1", "insight 2", "insight 3"]
                    """
                    
                    # Truncate content if too long
                    truncated_content = content[:10000] if content else "No content available"
                    
                    model = get_model()
                    formatted_prompt = ChatPromptTemplate.from_template(insights_prompt).format_messages(
                        topic=course_topic,
                        content=truncated_content
                    )
                    
                    try:
                        insights_response = model.invoke(formatted_prompt)
                        insights = parse_json(insights_response.content.replace("```json", "").replace("```", ""))
                        if isinstance(insights, list):
                            for insight in insights:
                                if insight not in enhanced_content["extracted_insights"]:
                                    enhanced_content["extracted_insights"].append(insight)
                    except Exception as e:
                        # raise
                        st.warning(f"Error extracting insights: {e}")
            
            progress_bar.empty()
        
        return enhanced_content

def enhanced_course_manager(course_topic, difficulty_level, target_audience, learning_goals, search_insights=[]):
    """Generate course structure with manager"""
    print("================manager started")
    model = get_model()
    
    # Enhanced manager template that includes search insights
    manager_template = """
    You are an expert course designer team manager with a PhD in instructional design and curriculum development.

    User requested a course on: {course_topic}
    Difficulty level: {difficulty_level}
    Target audience: {target_audience}
    Learning goals: {learning_goals}

    {insights_section}

    You are managing 4 specialized teams to create a comprehensive, expert-level course:

    1. Curriculum Planning Team: Responsible for overall structure, learning objectives, module sequencing
    2. Content Development Team: Responsible for developing main educational content, explanations, and core concepts
    3. Assessment Team: Responsible for exercises, quizzes, practice materials, and projects
    4. Resources Team: Responsible for supplementary materials, references, advanced topics, and glossaries

    Divide the course creation tasks among these teams in a way that ensures a cohesive, high-quality learning experience.
    Be specific about what each team should focus on for this particular course topic.

    Please create the tasks in a JSON format with the following structure:
    {format_instructions}

    Return ONLY the JSON without any additional text or explanation.
    """
    
    # Add insights section if available
    insights_section = ""
    if search_insights:
        insights_section = "Expert insights from research:\n" + "\n".join([f"- {insight}" for insight in search_insights])
    
    # Generate the prompt with the course content
    manager_parser = JsonOutputParser()
    manager_prompt = ChatPromptTemplate.from_template(manager_template)
    manager_prompt = manager_prompt.partial(format_instructions=manager_parser.get_format_instructions())
    
    formatted_prompt = manager_prompt.format_messages(
        course_topic=course_topic,
        difficulty_level=difficulty_level,
        target_audience=target_audience,
        learning_goals=learning_goals,
        insights_section=insights_section
    )
    
    # Get the model response
    with st.spinner("Planning course structure..."):
        model_response = model.invoke(formatted_prompt)
        # Parse the JSON response
        manager_output = parse_json(model_response.content)
        print("manager ends=================")
        
        return manager_output

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

async def generate_team_output(team_num, specialty, course_topic, difficulty_level, target_audience, learning_goals):
    """Generate team leader output"""
    print(f"Team {team_num} started...")
    model = get_model()
    team_template = """
    You are an expert course content developer specializing in {specialty} with years of experience creating professional educational content.

    Here is the task:
    - Create a course on: {course_topic}
    - Difficulty level: {difficulty_level}
    - Target audience: {target_audience}
    - Learning goals: {learning_goals}

    Your job is to propose three comprehensive, well-structured modules that fulfill your team's assignment for this course.
    Each module should have a clear title, concise description, and specific learning objectives.

    Return a JSON object with this structure:
    {format_instructions}
    
    Return ONLY the JSON without any additional text.
    """
    parser = JsonOutputParser(pydantic_object=Task)
    prompt = ChatPromptTemplate.from_template(team_template)
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    formatted_prompt = prompt.format_messages(
        specialty=specialty,
        course_topic=course_topic,
        difficulty_level=difficulty_level,
        target_audience=target_audience,
        learning_goals=learning_goals
    )
    
    with st.spinner(f"Team {team_num} creating modules for {specialty}..."):
        response = model.invoke(formatted_prompt)
        team_output = parse_json(response.content)
        properties = team_output.get("properties")
        if properties:
            team_output = properties

        team_structured_output = {f"team{team_num}": team_output}
        print(f"Team {team_num} Ended!")
        return team_structured_output

async def generate_module_content(module_title, module_description, learning_objectives, course_topic, difficulty_level, target_audience):
    """Generate extremely detailed content for a module"""
    print("Detailed Content Generation Module Started ...")
    model = get_model()
    content_template = """
    Create extremely detailed and comprehensive content for this module in a course about {course_topic}.
    Your goal is to create the most thorough, in-depth educational content possible.
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    IMPORTANT INSTRUCTIONS FOR DETAILED CONTENT:
    
    1. Introduction: Write a comprehensive 300+ word introduction that thoroughly explains the module's purpose, relevance, and what students will gain.
    
    2. Sections: Create 5-7 detailed sections. For EACH section:
       - Write a clear, descriptive title
       - Provide 400-600 words of detailed content with explanations, background information, and conceptual frameworks
       - Include 2-4 subsections for each section, each with 200+ words of specific content
       - Use examples, analogies, and explanations of underlying principles
    
    3. Key Concepts: Include 8-12 key concepts with detailed explanations (not just one-line definitions)
    
    4. Examples: For each of the 3-5 examples:
       - Provide a realistic scenario or context
       - Include a detailed 300+ word walkthrough with step-by-step explanations
       - Add 3-5 key takeaways from each example
    
    5. Practice Activities: Include 3-5 detailed practice activities with clear instructions and expected outcomes
    
    6. Summary: Write a comprehensive 250+ word summary that ties everything together
    
    7. Further Reading: Suggest 3-5 resources for deeper learning with brief descriptions
    
    Your content should be extremely detailed, providing depth equivalent to a high-quality textbook chapter or professional learning material. DO NOT provide short or superficial content.
    
    {format_instructions}
    """
    parser = JsonOutputParser(pydantic_object=ModuleContent)
    prompt = ChatPromptTemplate.from_template(content_template)
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating comprehensive content for module: {module_title}..."):
        # For very detailed content, we might need to increase the max_tokens
        response = model.invoke(formatted_prompt, temperature=0.7)
        content = parse_json(response.content)
        print("Detailed Content Generation Module Ended!")
        return content

async def generate_assessments(module_title, module_description, learning_objectives, course_topic, difficulty_level, target_audience):
    """Generate comprehensive detailed assessments for a module"""
    model = get_model()
    assessment_template = """
    Create extremely comprehensive and detailed assessments for this module in a course about {course_topic}.
    Your goal is to create assessment materials that thoroughly evaluate student understanding and provide detailed learning opportunities.
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    IMPORTANT INSTRUCTIONS FOR DETAILED ASSESSMENTS:
    
    1. Quiz Questions: Create 8-12 detailed quiz questions. For EACH question:
       - Write a detailed question (at least 50 words) that tests deeper understanding
       - Provide background context explaining why this question matters (100+ words)
       - Create detailed answer options that require careful consideration
       - Include a comprehensive explanation of the correct answer (150+ words)
    
    2. Practice Problems: Create 4-6 comprehensive practice problems. For EACH problem:
       - Write a detailed problem statement (200+ words)
       - Provide real-world context that makes the problem relevant
       - Include a step-by-step detailed solution with explanations (300+ words)
       - Provide progressive hints to support different learning levels
       - List key learning points students should take away
    
    3. Project Ideas: Create 3-5 detailed project proposals. For EACH project:
       - Provide a comprehensive description (300+ words)
       - List specific learning goals addressed
       - Include detailed step-by-step implementation guidelines
       - Specify required resources, evaluation criteria, and possible extensions
    
    4. Self-Assessment: Create thoughtful reflection questions with guidelines for self-evaluation
    
    5. Grading Rubrics: Provide detailed grading criteria for each major assessment
    
    Your assessments should be extremely detailed, challenging, and designed to promote deep learning. DO NOT provide superficial or simplistic assessment materials.
    
    {format_instructions}
    """
    parser = JsonOutputParser(pydantic_object=DetailedModuleAssessment)
    prompt = ChatPromptTemplate.from_template(assessment_template)
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating comprehensive assessments for module: {module_title}..."):
        response = model.invoke(formatted_prompt, temperature=0.7)
        assessments = parse_json(response.content)
        
        return assessments

async def generate_resources(module_title, module_description, learning_objectives, course_topic, difficulty_level, target_audience):
    """Generate extremely detailed resources for a module"""
    model = get_model()
    resources_template = """
    Create extremely comprehensive and detailed supplementary resources for this module in a course about {course_topic}.
    Your goal is to provide the most thorough and valuable supplementary materials possible.
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    IMPORTANT INSTRUCTIONS FOR DETAILED RESOURCES:
    
    1. Recommended Readings: Provide 5-8 detailed reading recommendations. For EACH reading:
       - Include author, title, and comprehensive description (150+ words)
       - Explain key topics covered and specific relevance to the module
       - Include difficulty level, time commitment, and discussion questions
    
    2. Advanced Topics: Describe 4-6 advanced topics. For EACH topic:
       - Provide a comprehensive description (250+ words)
       - List prerequisites, learning pathway, and specific resources
       - Explain real-world applications of this topic
    
    3. Tools and Resources: Detail 4-6 tools or resources. For EACH tool:
       - Write a detailed description (200+ words)
       - Include specific use cases relevant to the module
       - Provide a detailed getting started guide and alternatives
    
    4. Glossary: Create 10-15 detailed glossary items. For EACH term:
       - Write a comprehensive definition (50+ words)
       - Explain usage context and importance (75+ words)
       - Include examples and related terms
    
    5. Case Studies: Develop 2-4 detailed case studies. For EACH case:
       - Present a detailed real-world scenario (300+ words)
       - Provide in-depth analysis (400+ words)
       - Include key lessons and discussion questions
    
    6. Cheat Sheets: Create quick reference materials for key concepts
    
    Your resources should be extremely detailed, comprehensive, and valuable for different learning styles and depth of exploration. DO NOT provide superficial or limited resources.
    
    {format_instructions}
    """
    parser = JsonOutputParser(pydantic_object=DetailedModuleResources)
    prompt = ChatPromptTemplate.from_template(resources_template)
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating comprehensive resources for module: {module_title}..."):
        response = model.invoke(formatted_prompt, temperature=0.7)
        resources = parse_json(response.content)
        
        return resources    

async def generate_course_metadata(course_topic, difficulty_level, target_audience, learning_goals, team_outputs):
    """Generate course metadata"""
    model = get_model()
    metadata_template = """
    Create comprehensive course metadata for a course on {course_topic}.
    
    Difficulty level: {difficulty_level}
    Target audience: {target_audience}
    Learning goals: {learning_goals}
    
    Team outputs:
    {team_outputs}
    
    {format_instructions}
    """
    parser = JsonOutputParser(pydantic_object=CourseMetadata)
    prompt = ChatPromptTemplate.from_template(metadata_template)
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        difficulty_level=difficulty_level,
        target_audience=target_audience,
        learning_goals=learning_goals,
        team_outputs=json.dumps(team_outputs, indent=2)
    )
    
    with st.spinner("Creating course metadata..."):
        response = model.invoke(formatted_prompt)
        metadata = parse_json(response.content)
        
        return metadata

async def generate_course_async(form_data):
    """Main function to generate course"""
    job_id = str(uuid.uuid4())
    course_topic = form_data["topic"]
    difficulty_level = form_data["difficulty"]
    target_audience = form_data["target_audience"]
    learning_goals = form_data["learning_goals"]
    enhanced_search = form_data["enhanced_search"]
    
    # Initialize job
    st.session_state.jobs[job_id] = {
        "job_id": job_id,
        "status": "in_progress",
        "progress": 0,
        "current_stage": "Initializing",
        "course_topic": course_topic,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "course_data": {}
    }
    
    st.session_state.current_job_id = job_id
    
    course_data = {}
    search_results = {}
    
    try:
        # Step 1: Web search enhancement if enabled
        if enhanced_search:
            st.session_state.jobs[job_id]["current_stage"] = "Enhancing with web search"
            st.session_state.jobs[job_id]["progress"] = 10
            search_results = await web_search_enhancer(course_topic)
            course_data["search_results"] = search_results
            st.session_state.jobs[job_id]["progress"] = 20
        
        # Step 2: Course manager
        st.session_state.jobs[job_id]["current_stage"] = "Planning course structure"
        st.session_state.jobs[job_id]["progress"] = 30
        search_insights = search_results.get("extracted_insights", []) if search_results else []
        manager_output = enhanced_course_manager(
            course_topic, 
            difficulty_level, 
            target_audience, 
            learning_goals,
            search_insights
        )
        course_data["manager_output"] = manager_output
        st.session_state.jobs[job_id]["progress"] = 40
        
        # Step 3: Generate team outputs in parallel
        st.session_state.jobs[job_id]["current_stage"] = "Creating modules and content"
        tasks = [
            generate_team_output(1, "curriculum planning", course_topic, difficulty_level, target_audience, learning_goals),
            generate_team_output(2, "content development", course_topic, difficulty_level, target_audience, learning_goals),
            generate_team_output(3, "assessments", course_topic, difficulty_level, target_audience, learning_goals),
            generate_team_output(4, "resources", course_topic, difficulty_level, target_audience, learning_goals)
        ]
        team_results = await asyncio.gather(*tasks)
        
        course_data["team_output_1"] = team_results[0]
        course_data["team_output_2"] = team_results[1]
        course_data["team_output_3"] = team_results[2]
        course_data["team_output_4"] = team_results[3]
        st.session_state.jobs[job_id]["progress"] = 60
        
        # Step 4: Generate specific content for first modules
        team1_module = team_results[0].get("team1", {})
        team2_module = team_results[1].get("team2", {})
        
        module1_title = team1_module.get("module_1", "")
        module1_desc = team1_module.get("description_1", "")
        module1_obj = team1_module.get("learning_objectives_1", [])
        
        module2_title = team2_module.get("module_1", "")
        module2_desc = team2_module.get("description_1", "")
        module2_obj = team2_module.get("learning_objectives_1", [])
        
        # Generate content, assessments and resources
        content_tasks = [
            generate_module_content(
                module1_title, module1_desc, module1_obj, 
                course_topic, difficulty_level, target_audience
            ),
            generate_module_content(
                module2_title, module2_desc, module2_obj, 
                course_topic, difficulty_level, target_audience
            ),
            generate_assessments(
                module1_title, module1_desc, module1_obj,
                course_topic, difficulty_level, target_audience
            ),
            generate_resources(
                module1_title, module1_desc, module1_obj,
                course_topic, difficulty_level, target_audience
            )
        ]
        
        st.session_state.jobs[job_id]["current_stage"] = "Creating detailed content"
        st.session_state.jobs[job_id]["progress"] = 70
        content_results = await asyncio.gather(*content_tasks)
        
        course_data["team1_module1"] = content_results[0]
        course_data["team2_module1"] = content_results[1]
        course_data["assessment_content"] = {"team1_module1": content_results[2]}
        course_data["resources_content"] = {"team1_module1": content_results[3]}
        
        st.session_state.jobs[job_id]["progress"] = 85
        
        # Step 5: Generate course metadata
        st.session_state.jobs[job_id]["current_stage"] = "Finalizing course structure"
        metadata = await generate_course_metadata(
            course_topic, 
            difficulty_level, 
            target_audience, 
            learning_goals,
            {
                "team1": team_results[0].get("team1", {}),
                "team2": team_results[1].get("team2", {}),
                "team3": team_results[2].get("team3", {}),
                "team4": team_results[3].get("team4", {})
            }
        )
        course_data["metadata"] = metadata
        
        # Save the course data
        save_course_to_file(job_id, course_data)
        
        # Update job status
        st.session_state.jobs[job_id]["status"] = "completed"
        st.session_state.jobs[job_id]["progress"] = 100
        st.session_state.jobs[job_id]["current_stage"] = "Course generation complete"
        st.session_state.jobs[job_id]["completed_at"] = datetime.now().isoformat()
        st.session_state.jobs[job_id]["course_data"] = course_data
        st.session_state.course_data = course_data
        
    except Exception as e:
        st.session_state.jobs[job_id]["status"] = "failed"
        st.session_state.jobs[job_id]["current_stage"] = f"Error: {str(e)}"
        st.error(f"An error occurred: {str(e)}")

# ---------------- Course Creation Tab ----------------

with tab1:
    st.header("Create a New Course")
    
    # Course creation form
    with st.form("course_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topic = st.text_input("Course Topic", placeholder="e.g., Machine Learning for Beginners")
            target_audience = st.text_input("Target Audience", 
                                         value="Adult learners interested in the subject",
                                         placeholder="e.g., College students interested in computer science")
            
        with col2:
            difficulty = st.selectbox("Difficulty Level", 
                                  options=["Beginner", "Intermediate", "Advanced", "Expert"],
                                  index=1)
            enhanced_search = st.checkbox("Enhance with web search", value=True)
        
        # Learning goals
        st.subheader("Learning Goals")
        default_goals = ["Understand core concepts", "Apply knowledge practically", "Develop critical thinking skills"]
        
        learning_goals = []
        for i, default in enumerate(default_goals):
            goal = st.text_input(f"Goal {i+1}", value=default, key=f"goal_{i}")
            if goal:
                learning_goals.append(goal)
        
        # Additional goals
        new_goal = st.text_input("Add another goal (optional)")
        if new_goal:
            learning_goals.append(new_goal)
            
        # Submit button
        submitted = st.form_submit_button("Generate Course", type="primary")
    
    # Handle form submission
    if submitted:
        if not topic:
            st.error("Please enter a course topic.")
        else:
            form_data = {
                "topic": topic,
                "difficulty": difficulty,
                "target_audience": target_audience,
                "learning_goals": learning_goals,
                "enhanced_search": enhanced_search
            }
            
            # Start course generation in a new thread
            st.markdown("### Course Generation Started")
            st.info("Please be patient while we generate your course. This may take several minutes.")
            
            # Create a placeholder for progress updates
            progress_container = st.empty()
            
            # Start the course generation
            asyncio.run(generate_course_async(form_data))
            
            # Show course generation is complete
            if st.session_state.current_job_id in st.session_state.jobs:
                job = st.session_state.jobs[st.session_state.current_job_id]
                if job["status"] == "completed":
                    st.success("Course generation complete!")
                    st.button("View Course", on_click=lambda: st.switch_page("pages/course_details.py"))
    
    # Show progress if a job is in progress
    if st.session_state.current_job_id and st.session_state.current_job_id in st.session_state.jobs:
        job = st.session_state.jobs[st.session_state.current_job_id]
        
        if job["status"] == "in_progress":
            st.markdown("### Course Generation Progress")
            st.progress(job["progress"] / 100)
            st.info(f"Current stage: {job['current_stage']}")
            
            # Auto-refresh the page
            time.sleep(1)
            st.experimental_rerun()

# ---------------- My Courses Tab ----------------

with tab2:
    st.header("My Courses")
    
    # List all jobs
    jobs = list(st.session_state.jobs.values())
    
    if not jobs:
        st.info("You haven't created any courses yet. Go to the 'Create Course' tab to get started.")
    else:
        # Create a dataframe with job info
        job_data = []
        for job in jobs:
            job_data.append({
                "ID": job["job_id"],
                "Course Topic": job["course_topic"],
                "Status": job["status"].capitalize(),
                "Progress": job["progress"],
                "Created At": job["created_at"]
            })
        
        df = pd.DataFrame(job_data)
        
        # Show table with jobs
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Select a course to view
        selected_job_id = st.selectbox("Select a course to view details", 
                                      [j["job_id"] for j in jobs if j["status"] == "completed"],
                                      format_func=lambda x: [j["course_topic"] for j in jobs if j["job_id"] == x][0])
        
        if selected_job_id:
            st.session_state.current_job_id = selected_job_id
            if st.button("View Selected Course"):
                # Load the course data
                job = st.session_state.jobs[selected_job_id]
                if "course_data" in job and job["course_data"]:
                    st.session_state.course_data = job["course_data"]
                else:
                    # Try to load from file
                    filename = f"courses/course_{selected_job_id}.json"
                    if os.path.exists(filename):
                        st.session_state.course_data = load_course_from_file(filename)
                    
                st.switch_page("pages/course_details.py")

# ---------------- About Tab ----------------

with tab3:
    st.header("About Advanced Course Generator")
    
    st.markdown("""
    ### Overview
    
    The Advanced Course Generator is a powerful tool that uses AI to create comprehensive, expert-level courses on any topic.
    
    ### Features
    
    - **Web-Enhanced Content**: Optionally enrich course content with current best practices and resources from the web
    - **Comprehensive Structure**: Creates complete course structure with modules, learning objectives, and content
    - **Rich Content**: Generates detailed content including examples, assessments, and supplementary resources
    - **Interactive Visualizations**: View course structure and content with intuitive visualizations
    - **Easy Editing**: Modify and enhance the generated content to fit your needs
    
    ### How It Works
    
    1. Enter your course topic, difficulty level, target audience, and learning goals
    2. Optionally enable web search to enhance content with current best practices
    3. The system generates a complete course structure with detailed content
    4. Review and edit the course as needed
    5. Export or use the course in your preferred learning management system
    
    ### Technologies Used
    
    - **LangChain**: For orchestrating AI interactions
    - **Streamlit**: For the user interface
    - **Plotly**: For interactive visualizations
    - **Web Search**: For enhancing content with current information
    """)