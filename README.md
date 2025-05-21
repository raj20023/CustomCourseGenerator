# Advanced Course Generator

This Streamlit application allows you to generate comprehensive, expert-level courses on any topic using AI. The application leverages LangChain, Ollama, and web search to create detailed course content.

## Features

- **Course Generation**: Create professional-quality courses with just a few inputs
- **Web Search Integration**: Optionally enhance content with current best practices and information from the web
- **Interactive Visualizations**: View course structure and content with intuitive visualizations
- **Content Editing**: Easily modify and enhance the generated content
- **Analytics**: Get insights into your course structure and content distribution

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install streamlit langchain langchain_openai langchain_core plotly pandas httpx
```

3. Add OPENAI_API_KEY in the .env file
4. If you want to use web search enhancement, get a Tavily API key and update it in the app.py file

## Project Structure

```
advanced_course_generator/
├── app.py                   # Main application file
├── pages/                   # Additional pages
│   ├── course_details.py    # Course details and visualizations
│   ├── edit_module.py       # Module content editing
│   └── edit_metadata.py     # Course metadata editing
├── courses/                 # Generated course files
└── README.md                # Documentation
```

## How to Run

```bash
streamlit run app.py
```

## Usage

1. Go to the "Create Course" tab
2. Enter your course details:
   - Course topic
   - Difficulty level
   - Target audience
   - Learning goals
3. Optionally enable web search enhancement
4. Click "Generate Course"
5. Wait for the course generation to complete
6. View and edit the generated course content
7. Export the course as JSON for use in your preferred learning management system

## Course Generation Process

The application follows these steps to generate a course:

1. **Web Research** (optional): Searches the web for current best practices and content related to the course topic
2. **Course Planning**: Divides the work among specialized teams for curriculum, content, assessments, and resources
3. **Module Creation**: Generates detailed module outlines with learning objectives
4. **Content Development**: Creates comprehensive content including sections, key concepts, and examples
5. **Assessment Creation**: Generates quizzes, practice problems, and project ideas
6. **Resource Collection**: Compiles recommended readings, tools, and glossary terms
7. **Metadata Generation**: Creates complete course metadata with prerequisites and learning outcomes

## Example Uses

The Advanced Course Generator is perfect for:

- Educators creating new courses
- Training departments in companies
- Content creators needing structured educational content
- Self-learners organizing study materials
- Anyone wanting to create comprehensive learning resources

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
