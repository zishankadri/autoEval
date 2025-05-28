# Automated Exam Generation & Grading System

## Overview
This project automates the creation of exam question papers, grading of answers, and generation of personalized notes for students. It aims to make teachers' lives easier by saving time on repetitive tasks, allowing them to focus more on teaching.

## Features
- **Automatic Question Paper Generation**: Generate random or topic-specific question papers.
- **Automated Grading**: Grade multiple-choice, short-answer, and essay-type questions automatically.
- **Detailed Analysis**: Get insights into student performance, identifying weak areas for improvement.
- **Personalized Notes**: Generate custom notes for students who answered questions incorrectly, helping them review and improve.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/project-name.git
    cd project-name
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables (e.g., API keys, database credentials) by creating a `.env` file in the root directory.

4. Run the server:
    ```bash
    python manage.py runserver
    ```

## Usage

1. **Uploading Chapters from the Course Section**:
    - Navigate to the Course section.

    - Click the “+” button to add a new chapter.

    - Enter the chapter title, and upload relevant materials (PDFs, text, etc.).

    - Click Save to upload the chapter.

    - The system will automatically process the content and generate a set of questions, which will be stored and available during the question paper creation stage.
        

2. **Creating a Question Paper**:
    - Navigate to the MCQ section.

    - Click the “+” button to create a new question set.

    - Fill out the form with the desired subject, topic, and number of questions.

    - Click Generate to create the question paper, then download it as needed.
    
3. **Grading and Feedback**:
   - Upload scanned answer sheets.
   - The system automatically grades the answers and provides feedback.

4. **Analyzing Results**:
   - Identify areas of improvement for individual students or the class as a whole.

5. **Generating Notes**:
   - Based on incorrect answers, personalized notes are generated and can be sent to students.

## Technologies Used
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **AI Models**: NLP models for question generation, grading, and feedback
- **Database**: PostgreSQL (or any other preferred DB)
- **OCR**: For grading handwritten answers

## Challenges
- **AI Grading Accuracy**: Ensuring the AI models accurately grade answers, especially for subjective questions.
- **Question Variability**: Generating diverse and topic-appropriate questions for different subjects.
- **Data Privacy**: Handling sensitive student data securely and ensuring compliance with privacy regulations.

## Future Improvements
- Integrate with Learning Management Systems (LMS) for seamless usage.
- Enhance AI models to grade more complex essay-type questions.
- Add multilingual support for global usage.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
