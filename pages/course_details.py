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
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Course Structure", "Module Content", "Assessments", "Analytics"])
        
        # Course Structure Tab
        with tab1:
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
            
            # Create a network graph of the course structure
            if modules:
                # Create nodes for the graph
                nodes = [{"id": "Course", "label": metadata.get("title", "Course"), "level": 0}]
                edges = []
                
                # Add module nodes
                for i, module in enumerate(modules):
                    module_id = f"Module {i+1}"
                    nodes.append({
                        "id": module_id,
                        "label": module.get("title", f"Module {i+1}"),
                        "level": 1
                    })
                    edges.append({"from": "Course", "to": module_id})
                    
                    # Add components for each module
                    components = ["Content", "Assessments", "Resources"]
                    for comp in components:
                        comp_id = f"{module_id} - {comp}"
                        nodes.append({
                            "id": comp_id,
                            "label": comp,
                            "level": 2
                        })
                        edges.append({"from": module_id, "to": comp_id})
                
                # Create a Plotly figure for the network
                fig = go.Figure()
                
                # Create edge traces
                for edge in edges:
                    # Find node positions
                    source_node = next(node for node in nodes if node["id"] == edge["from"])
                    target_node = next(node for node in nodes if node["id"] == edge["to"])
                    
                    # Level-based positioning
                    source_level = source_node["level"]
                    target_level = target_node["level"]
                    
                    # Find nodes at same level to determine x position
                    same_level_sources = [n for n in nodes if n["level"] == source_level]
                    same_level_targets = [n for n in nodes if n["level"] == target_level]
                    
                    source_index = same_level_sources.index(source_node)
                    target_index = same_level_targets.index(target_node)
                    
                    source_x = source_index - len(same_level_sources) / 2
                    target_x = target_index - len(same_level_targets) / 2
                    
                    # Add edge
                    fig.add_trace(go.Scatter(
                        x=[source_x, target_x],
                        y=[source_level * -1, target_level * -1],
                        mode='lines',
                        line=dict(width=1, color='rgba(100, 100, 100, 0.5)'),
                        hoverinfo='none',
                        showlegend=False
                    ))
                
                # Create node traces for each level
                for level in range(3):
                    level_nodes = [node for node in nodes if node["level"] == level]
                    
                    if not level_nodes:
                        continue
                    
                    # Get x positions
                    x_pos = [i - len(level_nodes) / 2 for i in range(len(level_nodes))]
                    
                    # Color based on level
                    colors = ['#5c67de', '#34d399', '#f97316']
                    
                    # Add nodes
                    fig.add_trace(go.Scatter(
                        x=x_pos,
                        y=[level * -1] * len(level_nodes),
                        mode='markers+text',
                        marker=dict(
                            size=30,
                            color=colors[level],
                            line=dict(width=1, color='white')
                        ),
                        text=[node["label"] for node in level_nodes],
                        textposition='middle center',
                        textfont=dict(size=10, color='white'),
                        hoverinfo='text',
                        hovertext=[node["label"] for node in level_nodes],
                        showlegend=False
                    ))
                
                # Update layout
                fig.update_layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    title="Course Structure Network"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Module Content Tab
        with tab2:
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
                        with st.expander(f"{i+1}. {section.get('title', 'Untitled Section')}"):
                            st.markdown(section.get("content", "No content available"))
                
                # Key Concepts
                key_concepts = selected_content.get("key_concepts", [])
                if key_concepts:
                    st.subheader("Key Concepts")
                    for concept in key_concepts:
                        st.markdown(f"- {concept}")
                
                # Examples
                examples = selected_content.get("examples", [])
                if examples:
                    st.subheader("Examples")
                    for i, example in enumerate(examples):
                        with st.expander(f"Example {i+1}: {example.get('title', 'Untitled Example')}"):
                            st.markdown(example.get("content", "No content available"))
                
                # Summary
                st.subheader("Summary")
                st.markdown(selected_content.get("summary", "No summary available"))
                
                # Edit button
                if st.button("Edit Module Content"):
                    st.session_state.editing_module = selected_module
                    st.switch_page("pages/edit_module.py")
        
        # Assessments Tab
        with tab3:
            st.header("Assessments")
            
            # Get assessment content
            assessment_content = course_data.get("assessment_content", {})
            
            if not assessment_content:
                st.info("No assessment content available.")
            else:
                # Get first assessment
                first_assessment = next(iter(assessment_content.values()), {})
                
                # Quiz questions
                quiz_questions = first_assessment.get("quiz_questions", [])
                if quiz_questions:
                    st.subheader("Quiz Questions")
                    for i, question in enumerate(quiz_questions):
                        with st.expander(f"Question {i+1}: {question.get('question', 'Untitled Question')}"):
                            options = question.get("options", [])
                            correct = question.get("correct_answer", "")
                            
                            for option in options:
                                is_correct = option == correct
                                if is_correct:
                                    st.markdown(f"✅ **{option}** (Correct)")
                                else:
                                    st.markdown(f"◯ {option}")
                
                # Practice problems
                practice_problems = first_assessment.get("practice_problems", [])
                if practice_problems:
                    st.subheader("Practice Problems")
                    for i, problem in enumerate(practice_problems):
                        with st.expander(f"Problem {i+1}: {problem.get('problem', 'Untitled Problem')[:50]}..."):
                            st.markdown("**Problem:**")
                            st.markdown(problem.get("problem", "No problem statement available"))
                            st.markdown("**Solution:**")
                            st.markdown(problem.get("solution", "No solution available"))
                
                # Project ideas
                project_ideas = first_assessment.get("project_ideas", [])
                if project_ideas:
                    st.subheader("Project Ideas")
                    for i, project in enumerate(project_ideas):
                        with st.expander(f"Project {i+1}: {project.get('title', 'Untitled Project')}"):
                            st.markdown(project.get("description", "No description available"))
                
                # Self assessment
                self_assessment = first_assessment.get("self_assessment", [])
                if self_assessment:
                    st.subheader("Self Assessment Questions")
                    for i, question in enumerate(self_assessment):
                        st.markdown(f"{i+1}. {question}")
                
                # Resources
                st.subheader("Supplementary Resources")
                resources_content = course_data.get("resources_content", {})
                
                if resources_content:
                    first_resource = next(iter(resources_content.values()), {})
                    
                    # Recommended readings
                    readings = first_resource.get("recommended_readings", [])
                    if readings:
                        with st.expander("Recommended Readings"):
                            for reading in readings:
                                st.markdown(f"**{reading.get('title', 'Untitled')}**: {reading.get('description', '')}")
                    
                    # Advanced topics
                    advanced = first_resource.get("advanced_topics", [])
                    if advanced:
                        with st.expander("Advanced Topics"):
                            for topic in advanced:
                                st.markdown(f"**{topic.get('title', 'Untitled')}**: {topic.get('description', '')}")
                    
                    # Tools and resources
                    tools = first_resource.get("tools_and_resources", [])
                    if tools:
                        with st.expander("Tools & Resources"):
                            for tool in tools:
                                st.markdown(f"**{tool.get('name', 'Untitled')}**: {tool.get('description', '')}")
                    
                    # Glossary
                    glossary = first_resource.get("glossary", [])
                    if glossary:
                        with st.expander("Glossary"):
                            for term in glossary:
                                st.markdown(f"**{term.get('term', 'Untitled')}**: {term.get('definition', '')}")
        
        # Analytics Tab
        with tab4:
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
            
            # Learning curve visualization
            st.subheader("Learning Curve Visualization")
            
            # Create a learning curve showing the progression of complexity
            modules = metadata.get("modules", [])
            if modules:
                module_names = [m.get("title", f"Module {i+1}") for i, m in enumerate(modules)]
                complexity_values = [0.3, 0.5, 0.7, 0.9][:len(modules)]
                
                learning_data = pd.DataFrame({
                    'Module': module_names,
                    'Complexity': complexity_values,
                    'Knowledge': [0.2, 0.4, 0.7, 0.9][:len(modules)]
                })
                
                fig3 = go.Figure()
                
                # Add complexity curve
                fig3.add_trace(go.Scatter(
                    x=learning_data['Module'],
                    y=learning_data['Complexity'],
                    mode='lines+markers',
                    name='Content Complexity',
                    line=dict(color='#5c67de', width=3),
                    marker=dict(size=10)
                ))
                
                # Add knowledge curve
                fig3.add_trace(go.Scatter(
                    x=learning_data['Module'],
                    y=learning_data['Knowledge'],
                    mode='lines+markers',
                    name='Expected Knowledge',
                    line=dict(color='#34d399', width=3),
                    marker=dict(size=10)
                ))
                
                # Update layout
                fig3.update_layout(
                    title='Learning Progression Curve',
                    xaxis_title='Course Modules',
                    yaxis_title='Level (0-1)',
                    yaxis=dict(range=[0, 1]),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig3, use_container_width=True)
                
                # Learning outcomes vs assessments
                st.subheader("Learning Outcomes vs Assessments")
                
                # Get learning outcomes
                outcomes = metadata.get("learning_outcomes", [])
                if outcomes:
                    outcome_data = []
                    for i, outcome in enumerate(outcomes):
                        # Calculate match percentage (in a real app, this would be more sophisticated)
                        match_percentage = min(100, (quiz_count + problem_count) * 20)
                        outcome_data.append({
                            'Outcome': f"Outcome {i+1}",
                            'Description': outcome,
                            'Match': match_percentage
                        })
                    
                    outcome_df = pd.DataFrame(outcome_data)
                    
                    fig4 = px.bar(
                        outcome_df,
                        x='Outcome',
                        y='Match',
                        color='Match',
                        labels={'Match': 'Assessment Coverage (%)'},
                        title='Learning Outcomes Assessment Coverage',
                        color_continuous_scale='Viridis',
                        hover_data=['Description']
                    )
                    
                    fig4.update_layout(yaxis_range=[0, 100])
                    
                    st.plotly_chart(fig4, use_container_width=True)
        
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
            if st.button("Export Course"):
                # Create JSON for download
                json_str = json.dumps(course_data, indent=2)
                
                # Prepare filename
                filename = f"{metadata.get('title', 'course').replace(' ', '_').lower()}.json"
                
                # Create download button
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=filename,
                    mime="application/json"
                )