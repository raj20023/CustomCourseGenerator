from typing import Annotated, List, Dict, Any, Optional
import json
import re
import os
import ast
from datetime import datetime
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama  # Updated import path
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langgraph.channels import LastValue


class State(TypedDict):
    messages: Annotated[list, add_messages]
    course_topic: Annotated[str, LastValue]
    difficulty_level: Annotated[str, LastValue]
    target_audience: Annotated[str, LastValue]
    learning_goals: Annotated[List[str], LastValue]
    manager_output: Annotated[Dict[str, Any], LastValue]
    team_output_1: str
    team_output_2: str
    team_output_3: str
    team_output_4: str
    team1_module1: str
    team2_module1: str
    assessment_content: Annotated[Dict[str, Any], LastValue]
    resources_content: Annotated[Dict[str, Any], LastValue]
    feedback: Annotated[Dict[str, Any], LastValue]
    course_metadata: Annotated[Dict[str, Any], LastValue]



# Define schemas for different components
class Task(BaseModel):
    task_1: str = Field(description="Task for team 1 - Course structure and curriculum planning")
    detail_1: str = Field(description="Detailed description of team 1's task")
    task_2: str = Field(description="Task for team 2 - Core content development")
    detail_2: str = Field(description="Detailed description of team 2's task")
    task_3: str = Field(description="Task for team 3 - Assessments, exercises and practice materials")
    detail_3: str = Field(description="Detailed description of team 3's task")
    task_4: str = Field(description="Task for team 4 - Resources, references and advanced materials")
    detail_4: str = Field(description="Detailed description of team 4's task")


class TeamModules(BaseModel):
    module_1: str = Field(description="Title of module 1")
    description_1: str = Field(description="Brief description of module 1 content")
    learning_objectives_1: List[str] = Field(description="Learning objectives for module 1")
    module_2: str = Field(description="Title of module 2")
    description_2: str = Field(description="Brief description of module 2 content")
    learning_objectives_2: List[str] = Field(description="Learning objectives for module 2")
    module_3: str = Field(description="Title of module 3")
    description_3: str = Field(description="Brief description of module 3 content")
    learning_objectives_3: List[str] = Field(description="Learning objectives for module 3")


class ModuleContent(BaseModel):
    title: str = Field(description="Title of the module")
    introduction: str = Field(description="Introduction to the module topics")
    sections: List[Dict[str, str]] = Field(description="List of sections with title and content")
    key_concepts: List[str] = Field(description="List of key concepts covered")
    examples: List[Dict[str, str]] = Field(description="Practical examples with title and content")
    summary: str = Field(description="Summary of the module")


class AssessmentContent(BaseModel):
    module_title: str = Field(description="Title of the module this assessment is for")
    quiz_questions: List[Dict[str, Any]] = Field(description="List of quiz questions with options and answers")
    practice_problems: List[Dict[str, str]] = Field(description="List of practice problems with solutions")
    project_ideas: List[Dict[str, str]] = Field(description="List of project ideas with descriptions")
    self_assessment: List[str] = Field(description="Self-assessment questions")


class ResourcesContent(BaseModel):
    module_title: str = Field(description="Title of the module these resources are for")
    recommended_readings: List[Dict[str, str]] = Field(description="Recommended readings with title and description")
    advanced_topics: List[Dict[str, str]] = Field(description="Advanced topics with title and description")
    tools_and_resources: List[Dict[str, str]] = Field(description="Useful tools and resources")
    glossary: List[Dict[str, str]] = Field(description="Glossary of terms")


class CourseMetadata(BaseModel):
    title: str = Field(description="Full course title")
    description: str = Field(description="Comprehensive course description")
    target_audience: str = Field(description="Description of the intended audience")
    prerequisites: List[str] = Field(description="List of prerequisites for taking this course")
    learning_outcomes: List[str] = Field(description="Overall learning outcomes for the course")
    modules: List[Dict[str, str]] = Field(description="List of all modules with titles and descriptions")
    estimated_duration: str = Field(description="Estimated time to complete the course")
    difficulty_level: str = Field(description="Course difficulty level (Beginner, Intermediate, Advanced, Expert)")
    instructional_approach: str = Field(description="Description of the teaching approach")
    authors_note: str = Field(description="Note from the course creators")


class FeedbackModel(BaseModel):
    strengths: List[str] = Field(description="Strengths of the course content")
    areas_for_improvement: List[str] = Field(description="Areas that could be improved")
    content_accuracy: int = Field(description="Rating of content accuracy from 1-10")
    engagement_level: int = Field(description="Rating of engagement level from 1-10")
    clarity: int = Field(description="Rating of clarity from 1-10")
    overall_quality: int = Field(description="Overall quality rating from 1-10")
    recommendations: List[str] = Field(description="Specific recommendations for improvement")


# Initialize model
model = ChatOllama(model="llama3.1:8b")

# Initialize output parsers
manager_parser = JsonOutputParser(pydantic_object=Task)
team_parser = JsonOutputParser(pydantic_object=TeamModules)
content_parser = JsonOutputParser(pydantic_object=ModuleContent)
assessment_parser = JsonOutputParser(pydantic_object=AssessmentContent)
resources_parser = JsonOutputParser(pydantic_object=ResourcesContent)
metadata_parser = JsonOutputParser(pydantic_object=CourseMetadata)
feedback_parser = JsonOutputParser(pydantic_object=FeedbackModel)


# Create prompt templates
manager_template = """
You are an expert course designer team manager with a PhD in instructional design and curriculum development.

User requested a course on: {course_topic}
Difficulty level: {difficulty_level}
Target audience: {target_audience}
Learning goals: {learning_goals}

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

team_template = """
You are an expert course content developer specializing in {team_specialty} with years of experience creating professional educational content.

Here is the task received from the course manager:
Task: {team_task}
Description: {team_detail}

Course Information:
- Topic: {course_topic}
- Difficulty level: {difficulty_level}
- Target audience: {target_audience}
- Learning goals: {learning_goals}

Your job is to propose three comprehensive, well-structured modules that fulfill your team's assignment for this course.
Each module should:
- Have a clear, descriptive title
- Include a concise but thorough description
- List specific learning objectives that align with the overall course goals
- Follow a logical progression that builds expertise step by step

Strictly follow following instructions:
Please create the modules in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

content_template = """
You are an expert educational content creator specialized in producing clear, engaging, and thorough instructional materials.

You're creating content for the following module in a course about {course_topic}:

Module Title: {module_title}
Module Description: {module_description}
Learning Objectives: {learning_objectives}

Course Information:
- Difficulty level: {difficulty_level}
- Target audience: {target_audience}

Create comprehensive, engaging, and instructionally sound content for this module. The content should be:
- Expert-level but accessible to the specified target audience
- Well-structured with logical flow between concepts
- Rich with clear explanations and illuminating examples
- Focused on helping learners achieve the stated learning objectives

Your content should include an introduction, multiple well-organized sections, key concepts, practical examples, and a summary.

Strictly follow following instructions:
Please create the module content in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

assessment_template = """
You are an expert in educational assessment design, specialized in creating effective learning evaluations.

You're creating assessments for the following module in a course about {course_topic}:

Module Title: {module_title}
Module Description: {module_description}
Learning Objectives: {learning_objectives}

Course Information:
- Difficulty level: {difficulty_level}
- Target audience: {target_audience}

Create comprehensive assessment materials including:
- Quiz questions with multiple-choice options and correct answers
- Practice problems with detailed solutions
- Project ideas that apply the module's concepts
- Self-assessment reflection questions

The assessments should:
- Directly measure achievement of the learning objectives
- Progress from basic understanding to application and analysis
- Include a variety of question types and difficulty levels
- Provide opportunities for both validation of knowledge and deeper learning

Strictly follow following instructions:
Please create the assessment content in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

resources_template = """
You are an expert in educational resource curation and advanced materials development.

You're creating supplementary resources for the following module in a course about {course_topic}:

Module Title: {module_title}
Module Description: {module_description}
Learning Objectives: {learning_objectives}

Course Information:
- Difficulty level: {difficulty_level}
- Target audience: {target_audience}

Create comprehensive supplementary resources including:
- Recommended readings with brief descriptions
- Advanced topics for learners who want to go deeper
- Useful tools and resources related to the module content
- A glossary of important terms and concepts

The resources should:
- Extend learning beyond the core content
- Provide pathways for learners with different interests
- Include both beginner-friendly and advanced materials
- Reference high-quality, authoritative sources when appropriate

Strictly follow following instructions:
Please create the resources content in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

metadata_template = """
You are an expert course designer responsible for creating the final course metadata and structure.

You are integrating a comprehensive course on: {course_topic}

Review the modules created by the different teams:

Team 1 (Curriculum Planning) Modules:
{team1_modules}

Team 2 (Content Development) Modules:
{team2_modules}

Team 3 (Assessment) Modules:
{team3_modules}

Team 4 (Resources) Modules:
{team4_modules}

Course Information:
- Difficulty level: {difficulty_level}
- Target audience: {target_audience}
- Learning goals: {learning_goals}

Create comprehensive course metadata that:
- Provides a compelling course title and description
- Clearly defines prerequisites and learning outcomes
- Organizes all modules into a cohesive structure
- Estimates appropriate course duration
- Describes the instructional approach
- Includes an authentic "note from the authors"

Strictly follow following instructions:
Please create the course metadata in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

feedback_template = """
You are an expert educational quality reviewer with extensive experience evaluating curriculum and course materials.

You are reviewing content for a course on: {course_topic}

You have access to:
- Course metadata and structure
- Sample module content
- Assessment materials
- Supplementary resources

Based on these materials, provide a comprehensive quality review that:
- Identifies specific strengths of the course materials
- Pinpoints concrete areas for improvement
- Rates various quality dimensions on a scale of 1-10
- Offers specific recommendations for enhancing the course

Consider factors such as:
- Alignment with learning objectives
- Clarity of explanations
- Engagement and interactivity
- Assessment quality and alignment
- Comprehensiveness of resources
- Overall coherence and progression

Strictly follow following instructions:
Please create the feedback in a JSON format with the following structure:
{format_instructions}

Return ONLY the JSON without any additional text or explanation.
every key value of the json should be in the double quots only.
"""

# Set up all prompt templates with parsers
manager_prompt = ChatPromptTemplate.from_template(manager_template)
manager_prompt = manager_prompt.partial(format_instructions=manager_parser.get_format_instructions())
print(manager_prompt)

team_prompt = ChatPromptTemplate.from_template(team_template)
team_prompt = team_prompt.partial(format_instructions=team_parser.get_format_instructions())

content_prompt = ChatPromptTemplate.from_template(content_template)
content_prompt = content_prompt.partial(format_instructions=content_parser.get_format_instructions())

assessment_prompt = ChatPromptTemplate.from_template(assessment_template)
assessment_prompt = assessment_prompt.partial(format_instructions=assessment_parser.get_format_instructions())

resources_prompt = ChatPromptTemplate.from_template(resources_template)
resources_prompt = resources_prompt.partial(format_instructions=resources_parser.get_format_instructions())

metadata_prompt = ChatPromptTemplate.from_template(metadata_template)
metadata_prompt = metadata_prompt.partial(format_instructions=metadata_parser.get_format_instructions())

feedback_prompt = ChatPromptTemplate.from_template(feedback_template)
feedback_prompt = feedback_prompt.partial(format_instructions=feedback_parser.get_format_instructions())


def json_maker_bot(json_text):
    print("Json bot called")
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

    formatted_prompt = json_formator_prompt.format_messages(
            json_text=json_text,
        )
    
    model_response = model.invoke(formatted_prompt)

    return model_response.content.replace("```json", "").replace("```", "")


# Helper functions
def parse_json(text):
    """Helper function to extract and parse JSON from text"""
    try:
        # First try direct JSON parsing
        return json.loads(text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON using regex
        text = text.replace("```json", "").replace("```", "")
        # print(text)
        text = json_maker_bot(text)
        json_match = ast.literal_eval(text)
        if not json_match:
            raise ValueError("Could not find JSON in response")
        return json.loads(json.dumps(json_match))


def extract_course_parameters(state: State) -> dict:
    """Extract course parameters from user input"""
    user_input = state["messages"][0].content
    
    # Set default values
    params = {
        "course_topic": "",
        "difficulty_level": "Intermediate",
        "target_audience": "Adult learners interested in the subject",
        "learning_goals": ["Understand core concepts", "Apply knowledge practically", "Develop critical thinking skills"]
    }
    
    # Extract course topic (required)
    topic_match = re.search(r'course\s+on\s*:?\s*(.*?)(?:\.|$|with|for)', user_input, re.IGNORECASE)
    if topic_match:
        params["course_topic"] = topic_match.group(1).strip()
    else:
        # Fallback to using the whole message
        params["course_topic"] = user_input.strip()
    
    # Extract difficulty level (optional)
    difficulty_match = re.search(r'difficulty\s*:?\s*(beginner|intermediate|advanced|expert)', user_input, re.IGNORECASE)
    if difficulty_match:
        params["difficulty_level"] = difficulty_match.group(1).capitalize()
    
    # Extract target audience (optional)
    audience_match = re.search(r'audience\s*:?\s*(.*?)(?:\.|$)', user_input, re.IGNORECASE)
    if audience_match:
        params["target_audience"] = audience_match.group(1).strip()
    
    # Extract learning goals (optional)
    goals_match = re.search(r'goals\s*:?\s*(.*?)(?:\.|$)', user_input, re.IGNORECASE)
    if goals_match:
        goals_text = goals_match.group(1).strip()
        goals = [g.strip() for g in re.split(r'[,;]', goals_text)]
        if goals:
            params["learning_goals"] = goals
    
    return params


# Node functions
def initialize_state(state: State) -> State:
    """Initialize state with course parameters"""
    try:
        # Extract course parameters
        params = extract_course_parameters(state)
        
        # Update state with extracted parameters
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Initializing course generation for: {params['course_topic']}"}],
            "course_topic": params["course_topic"],
            "difficulty_level": params["difficulty_level"],
            "target_audience": params["target_audience"],
            "learning_goals": params["learning_goals"],
            "manager_output": {},
            "team_output_1": {},
            "team_output_2": {},
            "team_output_3": {},
            "team_output_4": {},
            "team1_module1": {},
            "team2_module1": {},
            "module_content": {},
            "assessment_content": {},
            "resources_content": {},
            "feedback": {},
            "course_metadata": {}
        }
    except Exception as e:
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in initialization: {str(e)}. Please try again."}],
            "course_topic": "",
            "difficulty_level": "Intermediate",
            "target_audience": "General audience",
            "learning_goals": [],
            "manager_output": {},
            "team_outputs": {},
            "module_content": {},
            "assessment_content": {},
            "resources_content": {},
            "feedback": {},
            "course_metadata": {}
        }


def course_manager(state: State) -> State:
    """Course manager that divides the work among teams"""
    try:
        # Get the course parameters
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        learning_goals = state["learning_goals"]
        
        # Generate the prompt with the course content
        formatted_prompt = manager_prompt.format_messages(
            course_topic=course_topic,
            difficulty_level=difficulty_level,
            target_audience=target_audience,
            learning_goals=learning_goals
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        # Parse the JSON response
        manager_output = parse_json(model_response.content)
        # Update state
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": "Course manager has divided the work into specialized tasks for each team."}],
            "course_topic": course_topic,
            "difficulty_level": difficulty_level,
            "target_audience": target_audience,
            "learning_goals": learning_goals,
            "manager_output": manager_output,
            "team_output_1": state["team_output_1"],
            "team_output_2": state["team_output_2"],
            "team_output_3": state["team_output_3"],
            "team_output_4": state["team_output_4"],
            "team1_module1": state["team1_module1"],
            "team2_module1": state["team2_module1"],
            "assessment_content": state["assessment_content"],
            "resources_content": state["resources_content"],
            "feedback": state["feedback"],
            "course_metadata": state["course_metadata"]
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in course manager: {str(e)}. Please try again."}],
            **state
        }


def team_leader(state: State, team_num: int, specialty: str) -> State:
    """Generic team leader function that can be used for any team"""
    try:
        # Get relevant task information
        print(f"Team Leader {team_num} Started")
        manager_output = state["manager_output"]
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        learning_goals = state["learning_goals"]
        properties = manager_output.get("properties", None)
        task_key = f"task_{team_num}"
        detail_key = f"detail_{team_num}"
        if properties:
            manager_output = properties
        team_task = manager_output.get(task_key)
        team_detail = manager_output.get(detail_key)
        
        if not team_task or not team_detail:
            raise ValueError(f"Missing {task_key} or {detail_key} in manager response")
        
        # Generate the prompt with the team task
        formatted_prompt = team_prompt.format_messages(
            team_specialty=specialty,
            team_task=team_task,
            team_detail=team_detail,
            course_topic=course_topic,
            difficulty_level=difficulty_level,
            target_audience=target_audience,
            learning_goals=learning_goals
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        # Parse the JSON response
        team_output = parse_json(model_response.content)
        
        # Update team outputs in state
        team_outputs = state[f"team_output_{team_num}"].copy()
        team_outputs[f"team{team_num}"] = team_output
        print(f"Team Leader {team_num} Finished")
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Team {team_num} has created module outlines for the {specialty} aspect of the course."}],
            f"team_output_{team_num}": team_outputs,
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in team {team_num} processing: {str(e)}. Please try again."}],
            **state
        }


def content_creator(state: State, team_num: int, module_num: int) -> State:
    """Create detailed content for a specific module"""
    try:
        # Get relevant information
        print(f"Content creation has started for team {team_num}")
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        team_outputs = state[f"team_output_{team_num}"]
        
        team_key = f"team{team_num}"
        if team_key not in team_outputs:
            raise ValueError(f"Missing output from {team_key}")
        
        team_output = team_outputs[team_key]
        team_properties = team_output.get("properties", None)
        if team_properties:
            team_output = team_properties
        module_title = team_output.get(f"module_{module_num}")
        module_description = team_output.get(f"description_{module_num}")
        learning_objectives = team_output.get(f"learning_objectives_{module_num}", [])
        
        if not module_title or not module_description:
            raise ValueError(f"Missing module information for {team_key}, module {module_num}")
        
        # Generate the prompt for content creation
        formatted_prompt = content_prompt.format_messages(
            course_topic=course_topic,
            module_title=module_title,
            module_description=module_description,
            learning_objectives=learning_objectives,
            difficulty_level=difficulty_level,
            target_audience=target_audience
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        
        # Parse the JSON response
        content_output = parse_json(model_response.content)
        
        # Update content outputs in state
        # module_content = state["module_content"].copy()
        content_key = f"{team_key}_module{module_num}"
        # module_content[content_key] = content_output
        print(f"Content creation has ended for team {team_num}")
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Created detailed content for module: {module_title}."}],
            f"team_output_{team_num}": team_outputs,
            content_key: content_output,
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in content creation: {str(e)}. Please try again."}],
            **state
        }


def assessment_creator(state: State, team_num: int, module_num: int) -> State:
    """Create assessments for a specific module"""
    try:
        print(f"Assessment creation has started!")
        # Get relevant information
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        team_outputs = state[f"team_output_{team_num}"]
        
        team_key = f"team{team_num}"
        if team_key not in team_outputs:
            raise ValueError(f"Missing output from {team_key}")
        
        team_output = team_outputs[team_key]
        team_properties = team_output.get("properties", None)
        if team_properties:
            team_output = team_properties
        module_title = team_output.get(f"module_{module_num}")
        module_description = team_output.get(f"description_{module_num}")
        learning_objectives = team_output.get(f"learning_objectives_{module_num}", [])
        
        if not module_title or not module_description:
            raise ValueError(f"Missing module information for {team_key}, module {module_num}")
        
        # Generate the prompt for assessment creation
        formatted_prompt = assessment_prompt.format_messages(
            course_topic=course_topic,
            module_title=module_title,
            module_description=module_description,
            learning_objectives=learning_objectives,
            difficulty_level=difficulty_level,
            target_audience=target_audience
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        
        # Parse the JSON response
        assessment_output = parse_json(model_response.content)
        
        # Update assessment outputs in state
        assessment_content = state["assessment_content"].copy()
        assessment_key = f"{team_key}_module{module_num}"
        assessment_content[assessment_key] = assessment_output
        print(f"Assessment creation has ended!")
        
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Created assessments for module: {module_title}."}],
            f"team_output_{team_num}": team_outputs,
            "assessment_content": assessment_content,
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in assessment creation: {str(e)}. Please try again."}],
            **state
        }


def resources_creator(state: State, team_num: int, module_num: int) -> State:
    """Create resources for a specific module"""
    try:
        # Get relevant information
        print("Resources creator has started....")
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        team_outputs = state[f"team_output_{team_num}"]
        
        team_key = f"team{team_num}"
        if team_key not in team_outputs:
            raise ValueError(f"Missing output from {team_key}")
        
        team_output = team_outputs[team_key]
        team_properties = team_output.get("properties", None)
        if team_properties:
            team_output = team_properties
        module_title = team_output.get(f"module_{module_num}")
        module_description = team_output.get(f"description_{module_num}")
        learning_objectives = team_output.get(f"learning_objectives_{module_num}", [])
        if not module_title or not module_description:
            raise ValueError(f"Missing module information for {team_key}, module {module_num}")
        
        # Generate the prompt for resources creation
        formatted_prompt = resources_prompt.format_messages(
            course_topic=course_topic,
            module_title=module_title,
            module_description=module_description,
            learning_objectives=learning_objectives,
            difficulty_level=difficulty_level,
            target_audience=target_audience
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        
        # Parse the JSON response
        resources_output = parse_json(model_response.content)
        
        # Update resources outputs in state
        resources_content = state["resources_content"].copy()
        resources_key = f"{team_key}_module{module_num}"
        resources_content[resources_key] = resources_output
        print("Resources creator has ended!")
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Created resources for module: {module_title}."}],
            "resources_content": resources_content,
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in resources creation: {str(e)}. Please try again."}],
            **state
        }


def course_metadata_creator(state: State) -> State:
    """Create final course metadata integrating all components"""
    try:
        # Get all necessary information
        print("Metadata creator has started...")
        course_topic = state["course_topic"]
        difficulty_level = state["difficulty_level"]
        target_audience = state["target_audience"]
        learning_goals = state["learning_goals"]
        team_output_1 = state["team_output_1"]
        team_output_2 = state["team_output_2"]
        team_output_3 = state["team_output_3"]
        team_output_4 = state["team_output_4"]
        
        # Generate the prompt for metadata creation
        formatted_prompt = metadata_prompt.format_messages(
            course_topic=course_topic,
            difficulty_level=difficulty_level,
            target_audience=target_audience,
            learning_goals=learning_goals,
            team1_modules=json.dumps(team_output_1),
            team2_modules=json.dumps(team_output_2),
            team3_modules=json.dumps(team_output_3),
            team4_modules=json.dumps(team_output_4)
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        
        # Parse the JSON response
        metadata_output = parse_json(model_response.content)
        print("Metadata creator has ended!")
        
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Created complete course metadata for: {metadata_output.get('title', course_topic)}."}],
            "course_topic": course_topic,
            "difficulty_level": difficulty_level,
            "target_audience": target_audience,
            "learning_goals": learning_goals,
            "manager_output": state["manager_output"],
            "team_output_1": team_output_1,
            "team_output_2": team_output_2,
            "team_output_3": team_output_3,
            "team_output_4": team_output_4,
            "team1_module1": state["team1_module1"],
            "team2_module1": state["team2_module1"],
            "assessment_content": state["assessment_content"],
            "resources_content": state["resources_content"],
            "feedback": state["feedback"],
            "course_metadata": metadata_output
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in metadata creation: {str(e)}. Please try again."}],
            **state
        }


def quality_reviewer(state: State) -> State:
    """Review course quality and provide feedback"""
    try:
        # Get relevant information
        print("QR started....")
        course_topic = state["course_topic"]
        course_metadata = state["course_metadata"]
        module_content = {"team1_module1": state["team1_module1"], "team2_module1": state["team2_module1"]}
        # Sample some content for review
        content_sample = next(iter(module_content.values())) if module_content else {}
        assessment_sample = next(iter(state["assessment_content"].values())) if state["assessment_content"] else {}
        resources_sample = next(iter(state["resources_content"].values())) if state["resources_content"] else {}
        
        # For simplicity, we'll just use the first available content
        review_materials = {
            "metadata": json.dumps(course_metadata, indent=2),
            "content_sample": json.dumps(content_sample, indent=2),
            "assessment_sample": json.dumps(assessment_sample, indent=2),
            "resources_sample": json.dumps(resources_sample, indent=2)
        }
        
        # Generate the prompt for feedback
        formatted_prompt = feedback_prompt.format_messages(
            course_topic=course_topic,
            **review_materials
        )
        
        # Get the model response
        model_response = model.invoke(formatted_prompt)
        # Parse the JSON response
        feedback_output = parse_json(model_response.content)
        print("QR Ends!")
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": "Quality review completed with detailed feedback."}],
            "course_topic": course_topic,
            "difficulty_level": state["difficulty_level"],
            "target_audience": state["target_audience"],
            "learning_goals": state["learning_goals"],
            "manager_output": state["manager_output"],
            "team_output_1": state["team_output_1"],
            "team_output_2": state["team_output_2"],
            "team_output_3": state["team_output_3"],
            "team_output_4": state["team_output_4"],
            "team1_module1": state["team1_module1"],
            "team2_module1": state["team2_module1"],
            "assessment_content": state["assessment_content"],
            "resources_content": state["resources_content"],
            "feedback": feedback_output,
            "course_metadata": state["course_metadata"]
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in quality review: {str(e)}. Please try again."}],
            **state
        }


def course_generator_summary(state: State) -> State:
    """Generate final summary of the course"""
    try:
        # Get all necessary information
        course_metadata = state["course_metadata"]
        feedback = state["feedback"]
        team_outputs = {"team_output_1": state["team_output_1"], "team_output_2": state["team_output_2"], "team_output_3": state["team_output_3"], "team_output_4": state["team_output_1"]}
        # Count content items
        module_content = {"team1_module1": state["team1_module1"], "team2_module1": state["team2_module1"]}
        content_count = len(module_content)
        assessment_count = len(state["assessment_content"])
        resources_count = len(state["resources_content"])
        
        # Create summary message
        title = course_metadata.get("title", state["course_topic"])
        description = course_metadata.get("description", "A comprehensive course")
        target_audience = course_metadata.get("target_audience", state["target_audience"])
        modules = course_metadata.get("modules", [])
        duration = course_metadata.get("estimated_duration", "Varies")
        
        # Format modules for display
        module_list = "\n".join([f"- {m.get('title', 'Module')}" for m in modules])
        
        # Format quality metrics
        quality_metrics = ""
        if feedback:
            metrics = [
                f"Content Accuracy: {feedback.get('content_accuracy', 'N/A')}/10",
                f"Engagement Level: {feedback.get('engagement_level', 'N/A')}/10",
                f"Clarity: {feedback.get('clarity', 'N/A')}/10",
                f"Overall Quality: {feedback.get('overall_quality', 'N/A')}/10"
            ]
            quality_metrics = "\n".join(metrics)
        
        # Create detailed summary
        summary = f"""
# Course Generation Complete: {title}

## Course Overview
{description}

## Target Audience
{target_audience}

## Course Modules
{module_list}

## Course Statistics
- Total Modules: {len(modules)}
- Content Modules Created: {content_count}
- Assessment Sets Created: {assessment_count}
- Resource Collections Created: {resources_count}
- Estimated Duration: {duration}

## Quality Assessment
{quality_metrics}

All course materials have been generated and are ready for use. The course includes detailed content, assessments, and supplementary resources for each module.

To export this course, you can save the complete state data which contains all course content and metadata.
"""
        
        # Save the course data to a file (optional)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"course_{timestamp}.json"
        
        course_data = {
            "metadata": course_metadata,
            "modules": team_outputs,
            "content": module_content,
            "assessments": state["assessment_content"],
            "resources": state["resources_content"],
            "feedback": feedback
        }
        
        try:
            os.makedirs("courses", exist_ok=True)
            with open(f"courses/{filename}", "w") as f:
                json.dump(course_data, f, indent=2)
            file_message = f"\nCourse data has been saved to: courses/{filename}"
        except Exception as e:
            file_message = f"\nNote: Could not save course data to file: {str(e)}"
        
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": summary + file_message}],
            **state
        }
    except Exception as e:
        raise
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": f"Error in generating summary: {str(e)}. However, all course content has been generated."}],
            **state
        }


# Create specialized team leader functions
def team1_leader(state: State) -> State:
    return team_leader(state, 1, "curriculum planning and course structure")


def team2_leader(state: State) -> State:
    return team_leader(state, 2, "core content development")


def team3_leader(state: State) -> State:
    return team_leader(state, 3, "assessments and practice materials")


def team4_leader(state: State) -> State:
    return team_leader(state, 4, "resources and advanced materials")


# Create specialized content creators
def team1_module1_content(state: State) -> State:
    return content_creator(state, 1, 1)


def team2_module1_content(state: State) -> State:
    return content_creator(state, 2, 1)


def team3_module1_assessment(state: State) -> State:
    return assessment_creator(state, 3, 1)


def team4_module1_resources(state: State) -> State:
    return resources_creator(state, 4, 1)


# Build the graph
def build_course_generation_graph():
    """Build and return the course generation workflow graph"""
    graph_builder = StateGraph(State)
    
    # Add initialization node
    graph_builder.add_node("initialize", initialize_state)
    
    # Add course manager node
    graph_builder.add_node("course_manager", course_manager)
    
    # Add team leader nodes
    graph_builder.add_node("team1_leader", team1_leader)
    graph_builder.add_node("team2_leader", team2_leader)
    graph_builder.add_node("team3_leader", team3_leader)
    graph_builder.add_node("team4_leader", team4_leader)
    
    # Add content creator nodes
    graph_builder.add_node("team1_module1_content", team1_module1_content)
    graph_builder.add_node("team2_module1_content", team2_module1_content)
    graph_builder.add_node("team3_module1_assessment", team3_module1_assessment)
    graph_builder.add_node("team4_module1_resources", team4_module1_resources)
    
    # Add metadata and review nodes
    graph_builder.add_node("metadata_creator", course_metadata_creator)
    graph_builder.add_node("quality_review", quality_reviewer)
    graph_builder.add_node("course_summary", course_generator_summary)
    
    # Define the workflow
    graph_builder.add_edge(START, "initialize")
    graph_builder.add_edge("initialize", "course_manager")
    
    # Connect manager to team leaders (parallel execution)
    graph_builder.add_edge("course_manager", "team1_leader")
    graph_builder.add_edge("course_manager", "team2_leader")
    graph_builder.add_edge("course_manager", "team3_leader")
    graph_builder.add_edge("course_manager", "team4_leader")
    
    # Connect team leaders to content creators
    graph_builder.add_edge("team1_leader", "team1_module1_content")
    graph_builder.add_edge("team2_leader", "team2_module1_content")
    graph_builder.add_edge("team3_leader", "team3_module1_assessment")
    graph_builder.add_edge("team4_leader", "team4_module1_resources")
    
    # Define conditions for when to move to metadata creation
    def all_teams_ready(state: State):
        """Check if all teams have completed their initial content"""
        team_outputs = state["team_outputs"]
        return all(f"team{i}" in team_outputs for i in range(1, 5))
    
    def check_content_readiness(state: State) -> State:
        """Check if all content is ready and direct workflow appropriately"""
        team1_module1 = state.get("team1_module1", {})
        team2_module1 = state.get("team2_module1", {})
        assessment_content = state.get("assessment_content", {})
        resources_content = state.get("resources_content", {})
        
        all_ready = (len(team1_module1) >= 1 and 
                    len(team2_module1) >= 1 and
                    len(assessment_content) >= 1 and 
                    len(resources_content) >= 1)
        
        return {
            "messages": state["messages"] + [{"role": "assistant", 
                        "content": "All content samples are ready. Proceeding to metadata creation."
                        if all_ready else "Still waiting for content samples to be ready."}],
            "all_content_ready": all_ready
        }

    graph_builder.add_node("check_readiness", check_content_readiness)

    # Connect all content creators to the readiness check
    for creator in ["team1_module1_content", "team2_module1_content", 
                    "team3_module1_assessment", "team4_module1_resources"]:
        graph_builder.add_edge(creator, "check_readiness")

    # Add conditional edge from readiness check to metadata creator
    graph_builder.add_conditional_edges(
        "check_readiness",
        lambda state: state.get("all_content_ready", False),
        {True: "metadata_creator", False: END}
    )

    def content_samples_ready(state: State):
        """Check if we have at least one content sample from each type"""
        team1_module1 = state["team1_module1"]
        team2_module1 = state["team2_module1"]
        assessment_content = state["assessment_content"]
        resources_content = state["resources_content"]
        print("======================================")
        print(team1_module1)
        print("======================================")
        print(team2_module1)
        print("======================================")
        print(assessment_content)
        print("======================================")
        print(resources_content)
        print("======================================")
        
        return (len(team1_module1) >= 1 and 
                len(team2_module1) >= 1 and
                len(assessment_content) >= 1 and 
                len(resources_content) >= 1)
    
    # Connect content creators to metadata creation when ready
    # for creator in [
    #     "team1_module1_content", "team2_module1_content",
    #     "team3_module1_assessment", "team4_module1_resources"
    # ]:
    #     graph_builder.add_conditional_edges(
    #         creator,
    #         content_samples_ready,
    #         {True: "metadata_creator", False: END}
    #     )
    
    # Connect metadata creator to quality review
    graph_builder.add_edge("metadata_creator", "quality_review")
    
    # Connect quality review to summary
    graph_builder.add_edge("quality_review", "course_summary")
    
    # Connect summary to end
    graph_builder.add_edge("course_summary", END)
    
    # Compile the graph
    return graph_builder.compile()


# Function to run the graph
def generate_expert_course(course_topic, difficulty="Intermediate", target_audience=None, learning_goals=None):
    """
    Generate a complete expert-level course on the specified topic.
    
    Args:
        course_topic (str): The main topic of the course
        difficulty (str): Difficulty level (Beginner, Intermediate, Advanced, Expert)
        target_audience (str): Description of the intended audience
        learning_goals (list): List of learning goals for the course
    
    Returns:
        dict: The complete course content and metadata
    """
    # Set default values
    if target_audience is None:
        target_audience = "Adult learners interested in the subject"
    
    if learning_goals is None:
        learning_goals = [
            "Understand core concepts and principles",
            "Apply knowledge in practical scenarios",
            "Develop critical thinking skills in the subject area"
        ]
    
    # Format the input message
    input_message = (
        f"Create an expert-level course on: {course_topic}. "
        f"Difficulty: {difficulty}. "
        f"Audience: {target_audience}. "
        f"Goals: {', '.join(learning_goals)}."
    )
    
    # Initialize the graph
    graph = build_course_generation_graph()
    # graph.get_graph().print_ascii()
    
    # Create initial state
    initial_state = {
        "messages": [{"role": "user", "content": input_message}],
        "course_topic": "",  # Will be extracted in initialize_state
        "difficulty_level": "",
        "target_audience": "",
        "learning_goals": [],
        "manager_output": {},
        "team_outputs": {},
        "module_content": {},
        "assessment_content": {},
        "resources_content": {},
        "feedback": {},
        "course_metadata": {}
    }
    
    # Run the graph
    print(f"Generating course on: {course_topic}...")
    final_state = graph.invoke(initial_state)
    print("Course generation complete!")
    team_outputs = {"team_output_1": final_state["team_output_1"], "team_output_2": final_state["team_output_2"], "team_output_3": final_state["team_output_3"], "team_output_4": final_state["team_output_1"]}
    module_content = {"team1_module1": final_state["team1_module1"], "team2_module1": final_state["team2_module1"]}

    # Return the full course data
    messages_list = []
    for msg in final_state.get("messages", []):
        messages_list.append(msg.content)
    return {
        "conversation": messages_list,
        "metadata": final_state.get("course_metadata", {}),
        "modules": final_state.get("team_outputs", {}),
        "content": final_state.get("module_content", {}),
        "assessments": final_state.get("assessment_content", {}),
        "resources": final_state.get("resources_content", {}),
        "feedback": final_state.get("feedback", {})
    }


# Function to save course to file
def save_course_to_file(course_data, filename=None):
    """Save the generated course to a JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        course_topic = course_data.get("metadata", {}).get("title", "course")
        course_topic = re.sub(r'[^\w\s-]', '', course_topic).replace(' ', '_').lower()
        filename = f"{course_topic}_{timestamp}.json"
    
    os.makedirs("courses", exist_ok=True)
    filepath = os.path.join("courses", filename)
    print(course_data)
    with open(filepath, "w") as f:
        json.dump(course_data, f, indent=2)
    
    print(f"Course saved to: {filepath}")
    return filepath


# Function to extract course content for a specific module
def extract_module_content(course_data, team_num, module_num):
    """
    Extract content for a specific module from the course data.
    
    Args:
        course_data (dict): The complete course data
        team_num (int): Team number (1-4)
        module_num (int): Module number (1-3)
        
    Returns:
        dict: The module content including metadata, content, assessments, and resources
    """
    team_key = f"team{team_num}"
    content_key = f"{team_key}_module{module_num}"
    
    # Get module metadata
    module_metadata = {}
    if team_key in course_data.get("modules", {}):
        module_title = course_data["modules"][team_key].get(f"module_{module_num}")
        module_desc = course_data["modules"][team_key].get(f"description_{module_num}")
        module_objectives = course_data["modules"][team_key].get(f"learning_objectives_{module_num}", [])
        
        module_metadata = {
            "title": module_title,
            "description": module_desc,
            "learning_objectives": module_objectives
        }
    
    # Get module content, assessments, and resources
    module_content = course_data.get("content", {}).get(content_key, {})
    module_assessments = course_data.get("assessments", {}).get(content_key, {})
    module_resources = course_data.get("resources", {}).get(content_key, {})
    
    return {
        "metadata": module_metadata,
        "content": module_content,
        "assessments": module_assessments,
        "resources": module_resources
    }


# Example usage
if __name__ == "__main__":
    # Generate a course on machine learning
    course_data = generate_expert_course(
        course_topic="Machine Learning for Healthcare Applications",
        difficulty="Advanced",
        target_audience="Healthcare professionals and data scientists",
        learning_goals=[
            "Understand machine learning concepts relevant to healthcare",
            "Apply ML techniques to real-world healthcare problems",
            "Develop ethical ML solutions for medical applications",
            "Evaluate and validate healthcare ML models"
        ]
    )
    
    # Save the course to a file
    save_course_to_file(course_data)
    
    # Print a summary
    print("\nCourse Generation Summary:")
    print("-" * 50)
    title = course_data.get("metadata", {}).get("title", "Machine Learning Course")
    modules = course_data.get("metadata", {}).get("modules", [])
    print(f"Title: {title}")
    print(f"Total Modules: {len(modules)}")
    print(f"Content Modules: {len(course_data.get('content', {}))}")
    print(f"Assessment Sets: {len(course_data.get('assessments', {}))}")
    print(f"Resource Collections: {len(course_data.get('resources', {}))}")