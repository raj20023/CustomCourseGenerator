import streamlit as st
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Edit Course Metadata",
    page_icon="📝",
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

# Function to save course data
def save_course_data(job_id, course_data):
    """Save the course data to a file"""
    # Update session state
    st.session_state.course_data = course_data
    
    # Save to file
    filename = f"courses/course_{job_id}.json"
    try:
        with open(filename, "w") as f:
            json.dump(course_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving course data: {str(e)}")
        return False

# Check if we have a current job ID and editing flag
if ("current_job_id" not in st.session_state or not st.session_state.current_job_id or
    "editing_metadata" not in st.session_state):
    st.warning("No course selected for editing. Please go back to the course details page.")
    if st.button("Back to Course Details"):
        st.switch_page("pages/course_details.py")
else:
    job_id = st.session_state.current_job_id
    course_data = load_course_data(job_id)
    
    if not course_data:
        st.error("Could not load course data.")
        if st.button("Back to Course Details"):
            st.switch_page("pages/course_details.py")
    else:
        # Get metadata
        metadata = course_data.get("metadata", {})
        
        if not metadata:
            st.error("Course metadata not found.")
            if st.button("Back to Course Details"):
                st.switch_page("pages/course_details.py")
        else:
            st.title("📝 Edit Course Metadata")
            
            # Create form for editing
            with st.form("edit_metadata_form"):
                # Basic course information
                st.subheader("Basic Course Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Course Title", value=metadata.get("title", ""))
                    target_audience = st.text_input("Target Audience", value=metadata.get("target_audience", ""))
                    difficulty_level = st.selectbox(
                        "Difficulty Level",
                        options=["Beginner", "Intermediate", "Advanced", "Expert"],
                        index=["Beginner", "Intermediate", "Advanced", "Expert"].index(metadata.get("difficulty_level", "Intermediate")) if metadata.get("difficulty_level") in ["Beginner", "Intermediate", "Advanced", "Expert"] else 1
                    )
                
                with col2:
                    estimated_duration = st.text_input("Estimated Duration", value=metadata.get("estimated_duration", ""))
                    instructional_approach = st.text_input("Instructional Approach", value=metadata.get("instructional_approach", ""))
                
                # Course description
                st.subheader("Course Description")
                description = st.text_area("Description", value=metadata.get("description", ""), height=150)
                
                # Prerequisites
                st.subheader("Prerequisites")
                prerequisites_text = st.text_area(
                    "Prerequisites (one per line)", 
                    value="\n".join(metadata.get("prerequisites", [])),
                    height=100
                )
                
                # Learning outcomes
                st.subheader("Learning Outcomes")
                learning_outcomes_text = st.text_area(
                    "Learning Outcomes (one per line)", 
                    value="\n".join(metadata.get("learning_outcomes", [])),
                    height=150
                )
                
                # Authors note
                st.subheader("Authors Note")
                authors_note = st.text_area("Authors Note", value=metadata.get("authors_note", ""), height=100)
                
                # Modules
                st.subheader("Course Modules")
                modules = metadata.get("modules", [])
                module_titles = []
                module_descriptions = []
                
                # Display each module
                for i, module in enumerate(modules):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        module_title = st.text_input(f"Module {i+1} Title", value=module.get("title", ""), key=f"module_title_{i}")
                        module_titles.append(module_title)
                    
                    with col2:
                        module_description = st.text_area(f"Module {i+1} Description", value=module.get("description", ""), height=100, key=f"module_desc_{i}")
                        module_descriptions.append(module_description)
                
                # Add new module button
                add_module = st.checkbox("Add a new module")
                if add_module:
                    new_module_title = st.text_input("New Module Title", key="new_module_title")
                    new_module_description = st.text_area("New Module Description", height=100, key="new_module_description")
                
                # Submit button
                submitted = st.form_submit_button("Save Changes", type="primary")
            
            # Handle form submission
            if submitted:
                # Update metadata
                updated_metadata = {
                    "title": title,
                    "description": description,
                    "target_audience": target_audience,
                    "difficulty_level": difficulty_level,
                    "estimated_duration": estimated_duration,
                    "instructional_approach": instructional_approach,
                    "prerequisites": [prereq.strip() for prereq in prerequisites_text.split("\n") if prereq.strip()],
                    "learning_outcomes": [outcome.strip() for outcome in learning_outcomes_text.split("\n") if outcome.strip()],
                    "authors_note": authors_note,
                    "modules": [
                        {"title": title, "description": description} 
                        for title, description in zip(module_titles, module_descriptions)
                        if title.strip()
                    ]
                }
                
                # Add new module if provided
                if add_module and new_module_title.strip():
                    updated_metadata["modules"].append({
                        "title": new_module_title,
                        "description": new_module_description
                    })
                
                # Update course data
                course_data["metadata"] = updated_metadata
                
                # Save changes
                if save_course_data(job_id, course_data):
                    st.success("Course metadata saved successfully!")
                    st.button("Back to Course Details", on_click=lambda: st.switch_page("pages/course_details.py"))
            
            # Cancel button (outside form)
            if st.button("Cancel", help="Discard changes and return to the course details page"):
                del st.session_state.editing_metadata
                st.switch_page("pages/course_details.py")