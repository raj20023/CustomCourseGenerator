import streamlit as st
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Edit Module Content",
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

# Check if we have a current job ID and editing module
if ("current_job_id" not in st.session_state or not st.session_state.current_job_id or
    "editing_module" not in st.session_state):
    st.warning("No module selected for editing. Please go back to the course details page.")
    if st.button("Back to Course Details"):
        st.switch_page("pages/course_details.py")
else:
    job_id = st.session_state.current_job_id
    selected_module = st.session_state.editing_module
    course_data = load_course_data(job_id)
    
    if not course_data:
        st.error("Could not load course data.")
        if st.button("Back to Course Details"):
            st.switch_page("pages/course_details.py")
    else:
        # Determine which module to edit
        module_key = "team1_module1" if "Module 1" in selected_module else "team2_module1"
        module_content = course_data.get(module_key, {})
        
        if not module_content:
            st.error("Module content not found.")
            if st.button("Back to Course Details"):
                st.switch_page("pages/course_details.py")
        else:
            st.title(f"📝 Edit Module: {module_content.get('title', 'Untitled')}")
            
            # Create form for editing
            with st.form("edit_module_form"):
                # Module title
                title = st.text_input("Module Title", value=module_content.get("title", ""))
                
                # Introduction
                st.subheader("Introduction")
                introduction = st.text_area("Introduction Text", value=module_content.get("introduction", ""), height=200)
                
                # Sections
                st.subheader("Sections")
                sections = module_content.get("sections", [])
                section_titles = []
                section_contents = []
                
                # Display each section
                for i, section in enumerate(sections):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        section_title = st.text_input(f"Section {i+1} Title", value=section.get("title", ""), key=f"section_title_{i}")
                        section_titles.append(section_title)
                    
                    with col2:
                        section_content = st.text_area(f"Section {i+1} Content", value=section.get("content", ""), height=150, key=f"section_content_{i}")
                        section_contents.append(section_content)
                
                # Add new section button
                add_section = st.checkbox("Add a new section")
                if add_section:
                    new_section_title = st.text_input("New Section Title", key="new_section_title")
                    new_section_content = st.text_area("New Section Content", height=150, key="new_section_content")
                
                # Key Concepts
                st.subheader("Key Concepts")
                key_concepts_text = st.text_area(
                    "Key Concepts (one per line)", 
                    value="\n".join(module_content.get("key_concepts", [])),
                    height=150
                )
                
                # Examples
                st.subheader("Examples")
                examples = module_content.get("examples", [])
                example_titles = []
                example_contents = []
                
                # Display each example
                for i, example in enumerate(examples):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        example_title = st.text_input(f"Example {i+1} Title", value=example.get("title", ""), key=f"example_title_{i}")
                        example_titles.append(example_title)
                    
                    with col2:
                        example_content = st.text_area(f"Example {i+1} Content", value=example.get("content", ""), height=150, key=f"example_content_{i}")
                        example_contents.append(example_content)
                
                # Add new example button
                add_example = st.checkbox("Add a new example")
                if add_example:
                    new_example_title = st.text_input("New Example Title", key="new_example_title")
                    new_example_content = st.text_area("New Example Content", height=150, key="new_example_content")
                
                # Summary
                st.subheader("Summary")
                summary = st.text_area("Summary Text", value=module_content.get("summary", ""), height=200)
                
                # Submit button
                submitted = st.form_submit_button("Save Changes", type="primary")
            
            # Handle form submission
            if submitted:
                # Update module content
                updated_module = {
                    "title": title,
                    "introduction": introduction,
                    "sections": [
                        {"title": title, "content": content} 
                        for title, content in zip(section_titles, section_contents)
                        if title.strip() and content.strip()
                    ],
                    "key_concepts": [concept.strip() for concept in key_concepts_text.split("\n") if concept.strip()],
                    "examples": [
                        {"title": title, "content": content} 
                        for title, content in zip(example_titles, example_contents)
                        if title.strip() and content.strip()
                    ],
                    "summary": summary
                }
                
                # Add new section if provided
                if add_section and new_section_title.strip() and new_section_content.strip():
                    updated_module["sections"].append({
                        "title": new_section_title,
                        "content": new_section_content
                    })
                
                # Add new example if provided
                if add_example and new_example_title.strip() and new_example_content.strip():
                    updated_module["examples"].append({
                        "title": new_example_title,
                        "content": new_example_content
                    })
                
                # Update course data
                course_data[module_key] = updated_module
                
                # Save changes
                if save_course_data(job_id, course_data):
                    st.success("Module content saved successfully!")
                    st.button("Back to Course Details", on_click=lambda: st.switch_page("pages/course_details.py"))
            
            # Cancel button (outside form)
            if st.button("Cancel", help="Discard changes and return to the course details page"):
                del st.session_state.editing_module
                st.switch_page("pages/course_details.py")