# Backend Installation Guide

## Project Overview

This backend application is built using Flask and provides an API for fetching museum data for the city of Münster. It uses a PostgreSQL database with PostGIS for spatial data.

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- I am using python 3.11
- PostgreSQL with PostGIS extension
- pip (Python package manager)
- virtualenv

---

## Step 1: Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/TripTailor-ifgi/backend
cd backend
```

---

## Step 2: Create and Activate a Virtual Environment

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

---

## Step 3: Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure Database Credentials

1. Open the `config.py` file in the `app` folder.

2. Update the database credentials in the `Config` class:

   ```python
   class Config:
       DB_HOST = "your-database-host"
       DB_NAME = "your-database-name"
       DB_USER = "your-database-username"
       DB_PASSWORD = "your-database-password"
       DB_PORT = 5432  # Default PostgreSQL port
   ```

3. Ensure your PostgreSQL database has the required table (`planet_osm_polygon`) with the relevant data.