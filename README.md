# Smart Teaching Assistance Application

## Overview
This is an advanced AI-powered teaching assistance application built with Streamlit that helps educators generate comprehensive lesson plans, detailed course notes, and provides an interactive question-answering system.

## Features

### 1. Lesson Plan Generation
- Upload a syllabus text file
- Select difficulty level (Btech, Mtech, PHD)
- Generate and customize lesson plans using AI
- Download lesson plans as DOCX files

### 2. Detailed Notes Creation
- Optional textbook PDF upload for context
- Generate comprehensive course notes
- Customizable AI generation parameters
- Download detailed notes as DOCX files

### 3. Interactive Q&A
- Ask questions about generated notes
- AI-powered contextual answers
- Adjustable response parameters

## Prerequisites

### System Requirements
- Python 3.8+
- Streamlit
- OpenAI API Key

### Required Dependencies
- streamlit
- python-docx
- openai
- embedchain
- pypdf
- streamlit-authenticator
- python-dotenv
- pyyaml

## Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/smart-teaching-assistance.git
cd smart-teaching-assistance
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
- Create a `.env` file in the project root
- Add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

5. Configure authentication
- Create `config.yaml` with user credentials and authentication settings

## Running the Application

```bash
streamlit run app.py
```

## Configuration

### Authentication
- Edit `config.yaml` to manage user credentials
- Supports preauthorized users
- Secure cookie-based authentication

### AI Generation Parameters
- Adjust temperature and max tokens for:
  - Lesson plan generation
  - Detailed notes creation
  - Question answering

## Security
- Secure user authentication
- Environment variable management
- API key protection

## Customization
- Easily modify difficulty levels
- Adjust AI generation parameters
- Extend functionality as needed

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License
MIT License

## Contact
Email here : jk422331@gmail.com
