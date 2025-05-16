import streamlit as st
import json
import time
import uuid
import pandas as pd
import os
import re
import httpx
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime

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
    return ChatOllama(model="llama3.1:8b")

# API keys (replace with your actual keys and use st.secrets in production)
SERPER_API_KEY = "1d9a523a7e8bece373dd783dd739b6f09050f671"  # Replace with actual key

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
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-Key": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"Error during search: {str(e)}")
        return {"error": str(e), "results": []}
        
async def fetch_webpage_content(url):
    """Fetch content from a webpage"""
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.text
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
            "results": search_results.get("organic", [])[:5],
            "extracted_insights": []
        }
        
        # Try to fetch content from top results
        if "organic" in search_results:
            progress_bar = st.progress(0)
            for i, result in enumerate(search_results["organic"][:3]):
                if "link" in result:
                    progress_bar.progress((i+1)/3)
                    st.write(f"Analyzing: {result.get('title', 'Source')}")
                    
                    content = await fetch_webpage_content(result["link"])
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
    """Generate detailed content for a module"""
    model = get_model()
    content_template = """
    Create detailed content for this module in a course about {course_topic}:
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    Return a JSON object with this structure:
    {
      "title": "Module title",
      "introduction": "Introduction paragraph",
      "sections": [
        {"title": "Section 1", "content": "Section content..."},
        {"title": "Section 2", "content": "Section content..."}
      ],
      "key_concepts": ["concept 1", "concept 2", "concept 3"],
      "examples": [
        {"title": "Example 1", "content": "Example details..."},
        {"title": "Example 2", "content": "Example details..."}
      ],
      "summary": "Summary paragraph"
    }
    
    Return ONLY the JSON without any additional text.
    """
    
    prompt = ChatPromptTemplate.from_template(content_template)
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating content for module: {module_title}..."):
        response = model.invoke(formatted_prompt)
        content = parse_json(response.content)
        
        return content

async def generate_assessments(module_title, module_description, learning_objectives, course_topic, difficulty_level, target_audience):
    """Generate assessments for a module"""
    model = get_model()
    assessment_template = """
    Create comprehensive assessments for this module in a course about {course_topic}:
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    Return a JSON object with this structure:
    {
      "module_title": "Module title",
      "quiz_questions": [
        {
          "question": "Question text",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer": "Option A"
        }
      ],
      "practice_problems": [
        {
          "problem": "Problem description",
          "solution": "Solution explanation"
        }
      ],
      "project_ideas": [
        {
          "title": "Project title",
          "description": "Project description"
        }
      ],
      "self_assessment": ["Question 1", "Question 2"]
    }
    
    Return ONLY the JSON without any additional text.
    """
    
    prompt = ChatPromptTemplate.from_template(assessment_template)
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating assessments for module: {module_title}..."):
        response = model.invoke(formatted_prompt)
        assessments = parse_json(response.content)
        
        return assessments

async def generate_resources(module_title, module_description, learning_objectives, course_topic, difficulty_level, target_audience):
    """Generate resources for a module"""
    model = get_model()
    resources_template = """
    Create comprehensive supplementary resources for this module in a course about {course_topic}:
    
    Module Title: {module_title}
    Module Description: {module_description}
    Learning Objectives: {learning_objectives}
    Difficulty Level: {difficulty_level}
    Target Audience: {target_audience}
    
    Return a JSON object with this structure:
    {
      "module_title": "Module title",
      "recommended_readings": [
        {
          "title": "Reading title",
          "description": "Reading description"
        }
      ],
      "advanced_topics": [
        {
          "title": "Topic title",
          "description": "Topic description"
        }
      ],
      "tools_and_resources": [
        {
          "name": "Tool name",
          "description": "Tool description"
        }
      ],
      "glossary": [
        {
          "term": "Term",
          "definition": "Definition"
        }
      ]
    }
    
    Return ONLY the JSON without any additional text.
    """
    
    prompt = ChatPromptTemplate.from_template(resources_template)
    formatted_prompt = prompt.format_messages(
        course_topic=course_topic,
        module_title=module_title,
        module_description=module_description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        target_audience=target_audience
    )
    
    with st.spinner(f"Creating resources for module: {module_title}..."):
        response = model.invoke(formatted_prompt)
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
    
    Return a JSON object with this structure:
    {
      "title": "Course title",
      "description": "Comprehensive course description",
      "target_audience": "Description of the intended audience",
      "prerequisites": ["prerequisite 1", "prerequisite 2"],
      "learning_outcomes": ["outcome 1", "outcome 2", "outcome 3"],
      "modules": [
        {"title": "Module 1", "description": "Module 1 description"},
        {"title": "Module 2", "description": "Module 2 description"}
      ],
      "estimated_duration": "Estimated completion time",
      "difficulty_level": "Course difficulty",
      "instructional_approach": "Description of teaching approach",
      "authors_note": "Note from the course creators"
    }
    
    Return ONLY the JSON without any additional text.
    """
    
    prompt = ChatPromptTemplate.from_template(metadata_template)
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