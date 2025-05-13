#!/usr/bin/env python3
"""
Expert Course Generator CLI

This script provides a simple command-line interface to the multi-agent course generation system.
Users can generate expert-level, customized courses on any topic with detailed content,
assessments, and resources.

Usage:
    python coursegen_cli.py
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
try:
    from enhanced_coursegen_multiagent import generate_expert_course, save_course_to_file
except ImportError:
    print("Error: Could not import enhanced_coursegen_multiagent module.")
    print("Make sure it's in the current directory or in your Python path.")
    sys.exit(1)


def get_user_input():
    """Get course parameters from user input"""
    print("\n📚 Expert Course Generator 📚")
    print("=" * 50)
    print("Create customized, expert-level courses on any topic.\n")
    
    # Get course topic
    course_topic = input("Enter course topic: ")
    
    # Get difficulty level
    print("\nSelect difficulty level:")
    print("1. Beginner")
    print("2. Intermediate")
    print("3. Advanced")
    print("4. Expert")
    difficulty_choice = input("Enter choice (1-4) [2]: ") or "2"
    
    difficulty_map = {
        "1": "Beginner",
        "2": "Intermediate",
        "3": "Advanced",
        "4": "Expert"
    }
    
    difficulty = difficulty_map.get(difficulty_choice, "Intermediate")
    
    # Get target audience
    target_audience = input("\nDescribe the target audience [Adult learners]: ") or "Adult learners"
    
    # Get learning goals
    print("\nEnter learning goals (one per line, blank line to finish):")
    learning_goals = []
    while True:
        goal = input(f"Goal {len(learning_goals) + 1} (or blank to finish): ")
        if not goal:
            break
        learning_goals.append(goal)
    
    # If no goals were entered, use defaults
    if not learning_goals:
        learning_goals = [
            "Understand core concepts and principles",
            "Apply knowledge in practical scenarios",
            "Develop critical thinking skills in the subject area"
        ]
    
    return {
        "course_topic": course_topic,
        "difficulty": difficulty,
        "target_audience": target_audience,
        "learning_goals": learning_goals
    }


def display_progress(start_time):
    """Display a progress indicator"""
    phases = [
        "Initializing course parameters",
        "Course manager dividing tasks",
        "Team leaders creating module outlines",
        "Content creators developing modules",
        "Assessment team creating exercises",
        "Resources team gathering materials",
        "Integrating course components",
        "Quality review in progress",
        "Finalizing course structure"
    ]
    
    for i, phase in enumerate(phases):
        elapsed = time.time() - start_time
        print(f"\r[{i+1}/{len(phases)}] {phase}... ({elapsed:.1f}s elapsed)", end="")
        time.sleep(2)  # This is just for demonstration, the actual process is asynchronous
    
    print("\r" + " " * 80, end="")  # Clear the line


def display_course_summary(course_data):
    """Display a summary of the generated course"""
    metadata = course_data.get("metadata", {})
    
    print("\n\n✅ Course Generation Complete!")
    print("=" * 50)
    
    title = metadata.get("title", "Generated Course")
    description = metadata.get("description", "")
    audience = metadata.get("target_audience", "")
    duration = metadata.get("estimated_duration", "")
    modules = metadata.get("modules", [])
    
    print(f"\n🎓 {title}")
    print(f"\n{description}\n")
    
    print(f"Target Audience: {audience}")
    print(f"Estimated Duration: {duration}")
    print(f"Total Modules: {len(modules)}")
    
    print("\nModules:")
    for i, module in enumerate(modules):
        print(f"  {i+1}. {module.get('title', 'Module')}")
    
    # Display quality ratings if available
    feedback = course_data.get("feedback", {})
    if feedback:
        print("\nQuality Assessment:")
        metrics = [
            ("Content Accuracy", "content_accuracy"),
            ("Engagement Level", "engagement_level"),
            ("Clarity", "clarity"), 
            ("Overall Quality", "overall_quality")
        ]
        
        for label, key in metrics:
            rating = feedback.get(key, "N/A")
            print(f"  {label}: {rating}/10")


def main():
    """Main function for the CLI interface"""
    parser = argparse.ArgumentParser(description="Generate expert-level courses using a multi-agent system")
    parser.add_argument("--topic", help="Course topic")
    parser.add_argument("--difficulty", choices=["Beginner", "Intermediate", "Advanced", "Expert"],
                        default="Intermediate", help="Course difficulty level")
    parser.add_argument("--audience", help="Target audience description")
    parser.add_argument("--goals", nargs="+", help="Learning goals (multiple allowed)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--interactive", action="store_true", help="Use interactive mode")
    
    args = parser.parse_args()
    
    # If interactive mode or no topic specified, get input interactively
    if args.interactive or not args.topic:
        params = get_user_input()
    else:
        params = {
            "course_topic": args.topic,
            "difficulty": args.difficulty,
            "target_audience": args.audience or "Adult learners",
            "learning_goals": args.goals or [
                "Understand core concepts",
                "Apply knowledge practically",
                "Develop critical thinking skills"
            ]
        }
    
    print("\nGenerating course...")
    print(f"Topic: {params['course_topic']}")
    print(f"Difficulty: {params['difficulty']}")
    print(f"Target Audience: {params['target_audience']}")
    print(f"Learning Goals: {', '.join(params['learning_goals'])}")
    print("\nThis may take a few minutes. Please wait...\n")
    
    # Show progress indicator
    start_time = time.time()
    
    # Try to display progress in a separate thread
    try:
        import threading
        progress_thread = threading.Thread(target=display_progress, args=(start_time,))
        progress_thread.daemon = True
        progress_thread.start()
    except ImportError:
        pass  # Threading not available, skip progress display
    
    # Generate the course
    course_data = generate_expert_course(
        course_topic=params['course_topic'],
        difficulty=params['difficulty'],
        target_audience=params['target_audience'],
        learning_goals=params['learning_goals']
    )
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    print(f"\rCourse generation completed in {elapsed_time:.1f} seconds.")
    
    # Save the course
    output_file = args.output
    saved_path = save_course_to_file(course_data, output_file)
    
    # Display summary
    display_course_summary(course_data)
    
    print(f"\nCourse has been saved to: {saved_path}")
    print("\nThank you for using the Expert Course Generator! 🎓")


if __name__ == "__main__":
    main()