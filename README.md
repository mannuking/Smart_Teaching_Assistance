# Smart Teaching Assistant

## Overview

Smart Teaching Assistant is an advanced AI-powered educational tool designed to help educators create comprehensive teaching materials with minimal effort. The application leverages Google's Gemini AI to transform simple syllabi into structured roadmaps, detailed lesson plans, and comprehensive lecture notes - all downloadable in standard document formats.

## Key Features

### 1. Syllabus-to-Roadmap Conversion
- Upload syllabus in TXT or PDF format
- Paste syllabus text directly
- Generate a structured hierarchical topic roadmap
- Edit and customize the roadmap before proceeding

### 2. Interactive Lesson Plan Generation
- Create comprehensive lesson plans based on roadmap
- Adjustable detail levels (Overview, Standard, In-Depth)
- Customizable AI creativity settings
- Structured content sections:
  - Learning Objectives
  - Key Concepts & Definitions
  - Instructional Content Outline
  - Engagement Strategies & Activities
  - Assessment Methods & Checkpoints
  - Potential Challenges & Misconceptions
  - ELI5 for Complex Concepts
  - Educator Notes

### 3. Detailed Notes Generation
- Transform lesson plans into comprehensive lecture notes
- Highlight specific topics for additional examples and focus
- Fully formatted DOCX output for professional use
- Structured according to educational best practices

### 4. Document Export
- All materials exportable as DOCX files
- Professionally formatted documents ready for use
- Preserves formatting, hierarchical structure and educational organization

## System Requirements

### Hardware
- Any modern computer capable of running a web browser
- Minimum 4GB RAM recommended
- Stable internet connection

### Software
- Python 3.8 or higher
- Required Python packages (see Installation section)
- Google API key with Gemini access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Smart_Teaching_Assistance.git
   cd Smart_Teaching_Assistance
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google API key**
   - Create a `.env` file in the project root directory
   - Add your Google API key to the file:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

5. **Run the application**
   ```bash
   streamlit run app3.py
   ```

## Usage Guide

### Step 1: Syllabus and Parameters
1. Choose whether to upload a file (TXT/PDF) or enter text directly
2. Enter the subject name (e.g., "Introduction to Artificial Intelligence")
3. Select the target difficulty level (Btech, Mtech, PHD)

### Step 2: Generate Roadmap
1. Click "Generate Roadmap" to create a structured topic map
2. Review and edit the generated roadmap if needed
3. Save your changes before proceeding

### Step 3: Generate & Edit Lesson Plan
1. Adjust the AI creativity level using the slider
2. Select detail level (Overview, Standard, In-Depth)
3. Click "Generate Lesson Plan" 
4. Edit any section of the generated plan as needed
5. Save your changes and download as DOCX if desired

### Step 4: Generate Detailed Notes
1. (Optional) Enter comma-separated topic IDs to emphasize (e.g., "T1.1, T2.3")
2. Adjust AI creativity for notes generation
3. Click "Generate Detailed Notes"
4. Download the resulting DOCX file

## Code Structure

The application follows a modular structure with several key components:

### Main Functions

#### Syllabus Processing
- `extract_text_from_pdf(pdf_file)`: Extracts text content from uploaded PDF files
- `generate_roadmap(subject, syllabus_text, difficulty_level, temperature)`: Creates a structured roadmap from syllabus text

#### Roadmap Handling
- `parse_roadmap(roadmap_text)`: Converts the roadmap text into a structured dictionary
- `build_prompt_with_hierarchy(subject, difficulty_level, topic_data, parent_topics_content, depth)`: Creates prompts for lesson plan generation

#### Lesson Plan Generation
- `generate_lesson_plan_chunk(subject, difficulty_level, topic_data, parent_topics_content, depth, temperature)`: Generates content for a specific chunk of the lesson plan
- `generate_lesson_plan_recursive(subject, roadmap_text, difficulty_level, temperature, depth_setting)`: Recursively generates the entire lesson plan
- `parse_structured_content(text_content, tags_dict)`: Parses structured content with predefined tags
- `reconstruct_markdown_from_structured(structured_data, tags_dict)`: Reconstructs markdown from parsed structured data

#### Notes Generation
- `create_lecture_notes_prompt(lesson_plan_entry_title, lesson_plan_entry_content, current_id, subject_name, difficulty_level, highlighted_topics, parent_topics_content)`: Creates prompts for lecture notes
- `generate_lecture_notes_chunk(lesson_plan_json_root, current_id, subject_name, difficulty_level, highlighted_topics, parent_topics_content, temperature)`: Generates notes for a specific chunk
- `create_detailed_notes_recursive(lesson_plan_json_root, subject_name, difficulty_level, highlighted_topics, temperature)`: Recursively generates detailed notes for all topics

#### Document Creation
- `create_docx_from_lesson_plan(lesson_plan_json, filename)`: Creates a DOCX file from the lesson plan
- `create_docx_from_parsed_elements(all_topics_data, filename, subject_name, difficulty_level)`: Creates a DOCX from parsed elements for notes

### User Interface Components
- `display_app_header()`: Sets up the app header and CSS styling
- `display_lesson_plan_for_editing(lesson_plan_json_root)`: Displays the lesson plan for editing
- `display_topic_editor(topic_data, level)`: Displays a topic editor for each topic level

## Extending the Application

### Adding New Features
1. Modify the appropriate section in app3.py
2. Ensure any new dependencies are added to requirements.txt
3. Test thoroughly before deployment

### Customizing the UI
- Edit the CSS in the `display_app_header()` function
- Add new UI components through Streamlit's widgets

### Modifying AI Parameters
- Adjust temperature settings for creativity control
- Customize prompts in the various prompt-building functions

## Troubleshooting

### Common Issues
- **API Key Errors**: Ensure your Google API key is correctly set in the .env file
- **PDF Extraction Failures**: Some PDFs may have security features preventing text extraction
- **Memory Issues**: For very large syllabi, consider breaking them into smaller sections

### Error Handling
The application includes comprehensive error handling through:
- Try-except blocks for all API calls
- User-friendly error messages
- Caching mechanisms to prevent redundant API calls

## Credits

This application uses the following technologies:
- Streamlit for the web interface
- Google's Gemini AI for content generation
- python-docx for document creation
- PyPDF for PDF text extraction

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions, issues, or contributions, please contact:
- Email: jk422331@gmail.com
- GitHub: [Your GitHub Profile](https://github.com/yourusername)
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License
MIT License

## Contact
Email here : jk422331@gmail.com
