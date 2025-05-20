import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os

# Set page config
st.set_page_config(
    page_title="Course Details",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load course data
def load_course_data(job_id):
    """Load course data from file or session state"""
    if "course_data" in st.session_state and st.session_state.course_data:
        return st.session_state.course_data
    
    # Try to load from file
    filename = f"courses/course_{job_id}.json"
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading course data: {str(e)}")
        return {}

# Display functions that avoid nested expanders
def display_section(section, index):
    """Display a section with subsections"""
    with st.expander(f"Section {index+1}: {section.get('title', 'Untitled Section')}"):
        st.markdown(section.get("content", "No content available"))
        
        # Display subsections if available
        subsections = section.get("subsections", [])
        if subsections:
            st.markdown("### Subsections")
            for i, subsection in enumerate(subsections):
                st.markdown(f"#### {index+1}.{i+1} {subsection.get('title', 'Untitled Subsection')}")
                st.markdown(subsection.get("content", "No content available"))
                st.markdown("---")

def display_example(example, index):
    """Display an example"""
    with st.expander(f"Example {index+1}: {example.get('title', 'Untitled Example')}"):
        # Display scenario if available
        scenario = example.get("scenario")
        if scenario:
            st.markdown("**Scenario:**")
            st.markdown(scenario)
        
        # Display content
        st.markdown("**Example Details:**")
        st.markdown(example.get("content", "No content available"))
        
        # Display key takeaways if available
        takeaways = example.get("key_takeaways", [])
        if takeaways:
            st.markdown("**Key Takeaways:**")
            for takeaway in takeaways:
                st.markdown(f"- {takeaway}")

def display_quiz_question(question, index):
    """Display a quiz question"""
    with st.expander(f"Question {index+1}: {question.get('question', '')[:80]}..."):
        # Display context if available
        context = question.get("context")
        if context:
            st.markdown("**Context:**")
            st.markdown(context)
        
        # Display full question
        st.markdown("**Question:**")
        st.markdown(question.get("question", "No question available"))
        
        # Display options
        options = question.get("options", [])
        correct = question.get("correct_answer", "")
        
        st.markdown("**Options:**")
        for option in options:
            is_correct = option == correct
            if is_correct:
                st.markdown(f"✅ **{option}** (Correct)")
            else:
                st.markdown(f"◯ {option}")
        
        # Display explanation if available
        explanation = question.get("explanation")
        if explanation:
            st.markdown("**Explanation:**")
            st.markdown(explanation)

def display_practice_problem(problem, index):
    """Display a practice problem"""
    with st.expander(f"Problem {index+1}: {problem.get('problem', '')[:80]}..."):
        # Display context if available
        context = problem.get("context")
        if context:
            st.markdown("**Context:**")
            st.markdown(context)
        
        # Display problem
        st.markdown("**Problem:**")
        st.markdown(problem.get("problem", "No problem statement available"))
        
        # Display hints if available
        hints = problem.get("hints", [])
        if hints:
            st.markdown("**Hints:**")
            for i, hint in enumerate(hints):
                st.markdown(f"**Hint {i+1}:** {hint}")
        
        # Display solution
        st.markdown("**Solution:**")
        st.markdown(problem.get("solution", "No solution available"))
        
        # Display learning points if available
        learning_points = problem.get("learning_points", [])
        if learning_points:
            st.markdown("**Key Learning Points:**")
            for point in learning_points:
                st.markdown(f"- {point}")

# Check if we have a current job ID
if "current_job_id" not in st.session_state or not st.session_state.current_job_id:
    st.warning("No course selected. Please go back to the main page to select or create a course.")
    if st.button("Back to Main Page"):
        st.switch_page("app.py")
else:
    job_id = st.session_state.current_job_id
    course_data = load_course_data(job_id)
    
    if not course_data:
        st.error("Could not load course data.")
        if st.button("Back to Main Page"):
            st.switch_page("app.py")
    else:
        # Get metadata
        metadata = course_data.get("metadata", {})
        
        # Course Details Page
        st.title(f"📚 {metadata.get('title', 'Course Details')}")
        
        # Metadata Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Course Information")
            st.markdown(f"**Description**: {metadata.get('description', 'No description available')}")
            st.markdown(f"**Difficulty**: {metadata.get('difficulty_level', 'N/A')}")
            st.markdown(f"**Estimated Duration**: {metadata.get('estimated_duration', 'N/A')}")
            st.markdown(f"**Target Audience**: {metadata.get('target_audience', 'N/A')}")
            
        with col2:
            st.subheader("Prerequisites & Outcomes")
            
            # Prerequisites
            prerequisites = metadata.get("prerequisites", [])
            if prerequisites:
                st.markdown("**Prerequisites**:")
                for prereq in prerequisites:
                    st.markdown(f"- {prereq}")
            else:
                st.markdown("**Prerequisites**: None specified")
            
            # Learning Outcomes
            outcomes = metadata.get("learning_outcomes", [])
            if outcomes:
                st.markdown("**Learning Outcomes**:")
                for outcome in outcomes:
                    st.markdown(f"- {outcome}")
            else:
                st.markdown("**Learning Outcomes**: None specified")
        
        # Main tabs
        tabs = st.tabs(["Course Structure", "Module Content", "Assessments", "Resources", "Analytics"])
        
        # Course Structure Tab
        with tabs[0]:
            st.header("Course Structure")
            
            # Get modules
            modules = metadata.get("modules", [])
            
            if not modules:
                st.info("No modules available in the course structure.")
            else:
                # Create expandable sections for each module
                for i, module in enumerate(modules):
                    with st.expander(f"Module {i+1}: {module.get('title', 'Untitled')}"):
                        st.markdown(f"**Description**: {module.get('description', 'No description available')}")
                        
                        # Try to find learning objectives
                        team1_output = course_data.get("team_output_1", {}).get("team1", {})
                        if team1_output:
                            objectives = team1_output.get(f"learning_objectives_{i+1}", [])
                            if objectives:
                                st.markdown("**Learning Objectives**:")
                                for obj in objectives:
                                    st.markdown(f"- {obj}")
            
            # Visualization of course structure
            st.subheader("Course Structure Visualization")
            
            # Create course structure flowchart
            modules_count = len(modules)
            module_names = [module.get("title", f"Module {i+1}") for i, module in enumerate(modules)]
            
            if modules_count > 0:
                # Create a simple Plotly figure showing course flow
                fig = go.Figure()
                
                # Add course node
                fig.add_trace(go.Scatter(
                    x=[0], 
                    y=[0],
                    mode='markers+text',
                    marker=dict(size=30, color='#5c67de'),
                    text=['Course'],
                    textposition='middle center',
                    textfont=dict(color='white'),
                    name='Course'
                ))
                
                # Add module nodes
                x_positions = [0 if modules_count == 1 else (i - (modules_count-1)/2) for i in range(modules_count)]
                y_positions = [-1] * modules_count
                
                fig.add_trace(go.Scatter(
                    x=x_positions, 
                    y=y_positions,
                    mode='markers+text',
                    marker=dict(size=25, color='#34d399'),
                    text=module_names,
                    textposition='middle center',
                    textfont=dict(color='white', size=10),
                    name='Modules'
                ))
                
                # Add lines connecting course to modules
                for i in range(modules_count):
                    fig.add_trace(go.Scatter(
                        x=[0, x_positions[i]],
                        y=[0, -1],
                        mode='lines',
                        line=dict(width=1, color='rgba(100, 100, 100, 0.5)'),
                        showlegend=False
                    ))
                
                # Update layout
                fig.update_layout(
                    showlegend=False,
                    title="Course Structure",
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        range=[-modules_count/2-0.5, modules_count/2+0.5]
                    ),
                    yaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        range=[-1.5, 0.5]
                    ),
                    height=300,
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Module Content Tab
        with tabs[1]:
            st.header("Module Content")
            
            # Get first module content
            module_content = course_data.get("team1_module1", {})
            
            if not module_content:
                st.info("No module content available.")
            else:
                # Module selector
                module_options = ["Module 1: " + module_content.get("title", "Untitled")]
                
                # Add module 2 if available
                module2_content = course_data.get("team2_module1", {})
                if module2_content:
                    module_options.append("Module 2: " + module2_content.get("title", "Untitled"))
                
                selected_module = st.selectbox("Select Module", module_options)
                
                # Show content based on selection
                selected_content = module_content if "Module 1" in selected_module else module2_content
                
                # Module content display
                st.subheader(selected_content.get("title", "Module Content"))
                
                # Introduction
                with st.expander("Introduction", expanded=True):
                    st.markdown(selected_content.get("introduction", "No introduction available"))
                
                # Sections
                sections = selected_content.get("sections", [])
                if sections:
                    st.subheader("Sections")
                    for i, section in enumerate(sections):
                        display_section(section, i)
                
                # Key Concepts
                key_concepts = selected_content.get("key_concepts", [])
                if key_concepts:
                    st.subheader("Key Concepts")
                    with st.expander("View All Key Concepts"):
                        for concept in key_concepts:
                            st.markdown(f"- {concept}")
                
                # Examples
                examples = selected_content.get("examples", [])
                if examples:
                    st.subheader("Examples")
                    for i, example in enumerate(examples):
                        display_example(example, i)
                
                # Practice Activities
                activities = selected_content.get("practice_activities", [])
                if activities:
                    st.subheader("Practice Activities")
                    for i, activity in enumerate(activities):
                        with st.expander(f"Activity {i+1}: {activity.get('title', 'Untitled Activity')}"):
                            st.markdown(activity.get("instructions", "No instructions available"))
                
                # Summary
                st.subheader("Summary")
                st.markdown(selected_content.get("summary", "No summary available"))
                
                # Further Reading
                further_reading = selected_content.get("further_reading", [])
                if further_reading:
                    st.subheader("Further Reading")
                    with st.expander("View Recommended Reading"):
                        for reading in further_reading:
                            st.markdown(f"**{reading.get('title', 'Untitled')}**: {reading.get('description', '')}")
        
        # Assessments Tab
        with tabs[2]:
            st.header("Assessments")
            
            # Get assessment content
            assessment_content = course_data.get("assessment_content", {})
            
            if not assessment_content:
                st.info("No assessment content available.")
            else:
                # Get first assessment
                first_assessment = next(iter(assessment_content.values()), {})
                
                assessment_subtabs = st.tabs(["Quiz Questions", "Practice Problems", "Projects", "Self-Assessment"])
                
                # Quiz questions tab
                with assessment_subtabs[0]:
                    quiz_questions = first_assessment.get("quiz_questions", [])
                    if quiz_questions:
                        st.subheader("Quiz Questions")
                        for i, question in enumerate(quiz_questions):
                            display_quiz_question(question, i)
                    else:
                        st.info("No quiz questions available.")
                
                # Practice problems tab
                with assessment_subtabs[1]:
                    practice_problems = first_assessment.get("practice_problems", [])
                    if practice_problems:
                        st.subheader("Practice Problems")
                        for i, problem in enumerate(practice_problems):
                            display_practice_problem(problem, i)
                    else:
                        st.info("No practice problems available.")
                
                # Projects tab
                with assessment_subtabs[2]:
                    project_ideas = first_assessment.get("project_ideas", [])
                    if project_ideas:
                        st.subheader("Project Ideas")
                        for i, project in enumerate(project_ideas):
                            with st.expander(f"Project {i+1}: {project.get('title', 'Untitled Project')}"):
                                st.markdown(project.get("description", "No description available"))
                                
                                # Display additional project details if available
                                for field in ["learning_goals", "steps", "resources_needed", "evaluation_criteria"]:
                                    items = project.get(field, [])
                                    if items:
                                        st.markdown(f"**{field.replace('_', ' ').title()}:**")
                                        for item in items:
                                            # Handle both string items and dict items
                                            if isinstance(item, dict):
                                                st.markdown(f"- **{item.get('title', '')}**: {item.get('description', '')}")
                                            else:
                                                st.markdown(f"- {item}")
                    else:
                        st.info("No project ideas available.")
                
                # Self-assessment tab
                with assessment_subtabs[3]:
                    self_assessment = first_assessment.get("self_assessment", [])
                    if self_assessment:
                        st.subheader("Self-Assessment Questions")
                        
                        # Handle different formats of self-assessment
                        if isinstance(self_assessment[0], dict):
                            for i, item in enumerate(self_assessment):
                                with st.expander(f"Question {i+1}: {item.get('question', 'Untitled')}"):
                                    st.markdown(item.get("guidelines", ""))
                        else:
                            for i, question in enumerate(self_assessment):
                                st.markdown(f"{i+1}. {question}")
                    else:
                        st.info("No self-assessment questions available.")
        
        # Resources Tab
        with tabs[3]:
            st.header("Resources")
            
            resources_content = course_data.get("resources_content", {})
            if not resources_content:
                st.info("No resources available.")
            else:
                first_resource = next(iter(resources_content.values()), {})
                
                resource_subtabs = st.tabs(["Readings", "Advanced Topics", "Tools", "Glossary", "Case Studies"])
                
                # Readings tab
                with resource_subtabs[0]:
                    readings = first_resource.get("recommended_readings", [])
                    if readings:
                        st.subheader("Recommended Readings")
                        for i, reading in enumerate(readings):
                            with st.expander(f"Reading {i+1}: {reading.get('title', 'Untitled')}"):
                                if reading.get("author"):
                                    st.markdown(f"**Author:** {reading.get('author')}")
                                
                                st.markdown(reading.get("description", "No description available"))
                                
                                # Display additional reading details if available
                                for field, label in [
                                    ("key_topics", "Key Topics"), 
                                    ("relevance", "Relevance"), 
                                    ("difficulty", "Difficulty")
                                ]:
                                    value = reading.get(field)
                                    if value:
                                        if isinstance(value, list):
                                            st.markdown(f"**{label}:**")
                                            for item in value:
                                                st.markdown(f"- {item}")
                                        else:
                                            st.markdown(f"**{label}:** {value}")
                    else:
                        st.info("No reading recommendations available.")
                
                # Advanced topics tab
                with resource_subtabs[1]:
                    advanced = first_resource.get("advanced_topics", [])
                    if advanced:
                        st.subheader("Advanced Topics")
                        for i, topic in enumerate(advanced):
                            with st.expander(f"Topic {i+1}: {topic.get('title', 'Untitled')}"):
                                st.markdown(topic.get("description", "No description available"))
                                
                                # Display additional topic details
                                for field, label in [
                                    ("prerequisites", "Prerequisites"), 
                                    ("learning_pathway", "Learning Pathway"), 
                                    ("applications", "Applications")
                                ]:
                                    value = topic.get(field)
                                    if value:
                                        if isinstance(value, list):
                                            st.markdown(f"**{label}:**")
                                            for item in value:
                                                st.markdown(f"- {item}")
                                        else:
                                            st.markdown(f"**{label}:** {value}")
                    else:
                        st.info("No advanced topics available.")
                
                # Tools tab
                with resource_subtabs[2]:
                    tools = first_resource.get("tools_and_resources", [])
                    if tools:
                        st.subheader("Tools & Resources")
                        for i, tool in enumerate(tools):
                            with st.expander(f"Tool {i+1}: {tool.get('name', 'Untitled')}"):
                                if tool.get("type"):
                                    st.markdown(f"**Type:** {tool.get('type')}")
                                
                                st.markdown(tool.get("description", "No description available"))
                                
                                # Display use cases if available
                                use_cases = tool.get("use_cases", [])
                                if use_cases:
                                    st.markdown("**Use Cases:**")
                                    for case in use_cases:
                                        st.markdown(f"- {case}")
                                
                                # Display getting started guide if available
                                getting_started = tool.get("getting_started")
                                if getting_started:
                                    st.markdown("**Getting Started:**")
                                    st.markdown(getting_started)
                    else:
                        st.info("No tools and resources available.")
                
                # Glossary tab
                with resource_subtabs[3]:
                    glossary = first_resource.get("glossary", [])
                    if glossary:
                        st.subheader("Glossary")
                        
                        # Search filter
                        search = st.text_input("Search glossary terms")
                        
                        # Filter items based on search
                        filtered_items = glossary
                        if search:
                            filtered_items = [item for item in glossary 
                                             if search.lower() in item.get("term", "").lower()]
                        
                        # Group items by first letter
                        grouped_items = {}
                        for item in filtered_items:
                            term = item.get("term", "")
                            if not term:
                                continue
                            first_letter = term[0].upper()
                            if first_letter not in grouped_items:
                                grouped_items[first_letter] = []
                            grouped_items[first_letter].append(item)
                        
                        # Display grouped items
                        if grouped_items:
                            letters = sorted(grouped_items.keys())
                            letter_tabs = st.tabs(letters)
                            
                            for i, letter in enumerate(letters):
                                with letter_tabs[i]:
                                    for item in grouped_items[letter]:
                                        st.markdown(f"**{item.get('term', 'Untitled')}**")
                                        st.markdown(item.get("definition", "No definition available"))
                                        
                                        # Display context if available
                                        context = item.get("context")
                                        if context:
                                            st.markdown("**Context:**")
                                            st.markdown(context)
                                        
                                        # Display examples if available
                                        examples = item.get("examples", [])
                                        if examples:
                                            st.markdown("**Examples:**")
                                            for example in examples:
                                                st.markdown(f"- {example}")
                                        
                                        st.markdown("---")
                        else:
                            st.info("No matching glossary terms found.")
                    else:
                        st.info("No glossary available.")
                
                # Case studies tab
                with resource_subtabs[4]:
                    cases = first_resource.get("case_studies", [])
                    if cases:
                        st.subheader("Case Studies")
                        for i, case in enumerate(cases):
                            with st.expander(f"Case Study {i+1}: {case.get('title', 'Untitled')}"):
                                # Display scenario
                                st.markdown("**Scenario:**")
                                st.markdown(case.get("scenario", "No scenario available"))
                                
                                # Display analysis
                                st.markdown("**Analysis:**")
                                st.markdown(case.get("analysis", "No analysis available"))
                                
                                # Display lessons and questions if available
                                for field, label in [("lessons", "Key Lessons"), ("questions", "Discussion Questions")]:
                                    items = case.get(field, [])
                                    if items:
                                        st.markdown(f"**{label}:**")
                                        for j, item in enumerate(items):
                                            if field == "questions":
                                                st.markdown(f"{j+1}. {item}")
                                            else:
                                                st.markdown(f"- {item}")
                    else:
                        st.info("No case studies available.")
        
        # Analytics Tab
        with tabs[4]:
            st.header("Course Analytics")
            
            # Count content items
            module_content = course_data.get("team1_module1", {})
            sections_count = len(module_content.get("sections", []))
            concepts_count = len(module_content.get("key_concepts", []))
            examples_count = len(module_content.get("examples", []))
            
            # Count assessment items
            assessment_content = next(iter(course_data.get("assessment_content", {}).values()), {})
            quiz_count = len(assessment_content.get("quiz_questions", []))
            problem_count = len(assessment_content.get("practice_problems", []))
            project_count = len(assessment_content.get("project_ideas", []))
            
            # Count resource items
            resource_content = next(iter(course_data.get("resources_content", {}).values()), {})
            readings_count = len(resource_content.get("recommended_readings", []))
            advanced_count = len(resource_content.get("advanced_topics", []))
            tools_count = len(resource_content.get("tools_and_resources", []))
            
            # Create analytics visualization
            col1, col2 = st.columns(2)
            
            with col1:
                # Content distribution chart
                content_data = pd.DataFrame({
                    'Type': ['Sections', 'Key Concepts', 'Examples'],
                    'Count': [sections_count, concepts_count, examples_count]
                })
                
                fig1 = px.bar(
                    content_data,
                    x='Type',
                    y='Count',
                    title='Content Distribution',
                    color='Type',
                    color_discrete_map={
                        'Sections': '#5c67de',
                        'Key Concepts': '#34d399',
                        'Examples': '#f97316'
                    }
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # Course metrics
                st.subheader("Course Metrics")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Total Modules", len(metadata.get("modules", [])))
                with cols[1]:
                    st.metric("Total Content Items", sections_count + concepts_count + examples_count)
                with cols[2]:
                    st.metric("Content to Assessment Ratio", 
                             f"{sections_count + concepts_count + examples_count}:{quiz_count + problem_count + project_count}")
            
            with col2:
                # Assessment distribution chart
                assessment_data = pd.DataFrame({
                    'Type': ['Quiz Questions', 'Practice Problems', 'Project Ideas'],
                    'Count': [quiz_count, problem_count, project_count]
                })
                
                fig2 = px.pie(
                    assessment_data,
                    values='Count',
                    names='Type',
                    title='Assessment Distribution',
                    color='Type',
                    color_discrete_map={
                        'Quiz Questions': '#8b5cf6',
                        'Practice Problems': '#ec4899',
                        'Project Ideas': '#f59e0b'
                    }
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Resource metrics
                st.subheader("Resource Metrics")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Readings", readings_count)
                with cols[1]:
                    st.metric("Advanced Topics", advanced_count)
                with cols[2]:
                    st.metric("Tools & Resources", tools_count)
            
        # Action buttons at the bottom
        st.write("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Back to Course List"):
                st.switch_page("app.py")
        
        with col2:
            if st.button("Edit Course Metadata"):
                st.session_state.editing_metadata = True
                st.switch_page("pages/edit_metadata.py")
        
        with col3:
            # Create JSON for download
            json_str = json.dumps(course_data, indent=2)
            
            # Prepare filename
            filename = f"{metadata.get('title', 'course').replace(' ', '_').lower()}.json"
            
            # Create download button
            st.download_button(
                label="Export Course",
                data=json_str,
                file_name=filename,
                mime="application/json"
            )