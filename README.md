# htn-2024-backend-developer-challenge

Hack the North 2024 Frontend Developer Challenge

# Startup Instructions

This repository contains a FastAPI application with SQLite database integration using SQLAlchemy.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a `Windows/Linux/Mac` machine.
- You have installed Python `3.6+`.

## Cloning the Repository

To clone this repository, run the following command in your terminal (or command prompt):

```bash
git clone https://github.com/Ri-Hong/htn-2024-backend-developer-challenge.git
```

## Installing Dependencies

To install the required dependencies, follow these steps:

1. Navigate to the project directory:

   ```bash
   cd htn-2024-backend-developer-challenge
   ```

2. Create a virtual environment:

   - For Windows:

     ```bash
     python -m venv venv
     ```

   - For macOS/Linux:

     ```bash
     python3 -m venv venv
     ```

3. Activate the virtual environment:

   - For Windows:

     ```bash
     .\venv\Scripts\activate
     ```

   - For macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

## Starting the Application

To start the FastAPI application, run the following command:

```bash
uvicorn app.main:app --reload
```

## Updating Dependencies

To update requirements.txt, run the following command:

```bash
pip freeze > requirements.txt
```

## Accessing the Application

After starting the application, you can access the API documentation at:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
