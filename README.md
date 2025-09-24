# FlexOne

Hackathon project creating a project onboarding tool for Flexday employees.

# Run the Application

Follow these steps to run the application:

## Prerequisites

- Python 3.7+ installed on your system

## Setup and Installation

1. **Create virtual environment**

   In your parent directory, create a virtual environment by:

   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**

   - **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the backend server**

   ```bash
   cd backend
   python application.py
   ```

2. **Launch the frontend** (in a new terminal window)
   ```bash
   cd frontend
   streamlit run app.py
   ```
