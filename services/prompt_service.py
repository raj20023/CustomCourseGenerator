JSON_FORMATOR_PROMPT = """
    You are an expert json issue resolver, you can make all json in proper format.

    Here is the json which dosen't have proper format of the json, Please make it in proper json format.
    {json_text}

    Strict Instructions:
    - return only corrected json format only.
    - don't give any other text then corrected json response.
    - *json needs to be 100 percent correct in the output.*
    """

INSIGHT_PROMPT = """
    Extract 3-5 key educational insights from this content that would be valuable for 
    creating a course on {topic}. Focus on teaching methodologies, important concepts,
    and best practices. Return the insights as a JSON array of strings.
    
    Content: {content}
    
    Strictly Return ONLY a JSON array like ["insight 1", "insight 2", "insight 3"]
    """

MANAGER_PROMPT = """
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

TEAM_PROMPT = """
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

CONTANT_PROMPT = """
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

ASSESSMENT_PROMPT = """
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

RESOURCE_PROMPT = """
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

METADATA_PROMPT = """
    Create comprehensive course metadata for a course on {course_topic}.
    
    Difficulty level: {difficulty_level}
    Target audience: {target_audience}
    Learning goals: {learning_goals}
    
    Team outputs:
    {team_outputs}
    
    {format_instructions}
    """

MARKDOWN_PROMPT = """
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
    """