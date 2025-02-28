# Backend (Trip Tailor)

## Project Overview

This backend application is of the [TripTailor](https://github.com/TripTailor-ifgi/TripTailor) project.

---

## Prerequisites

The following prerequisites are needed:

- Python 3.11
- PostgreSQL with PostGIS extension
- Docker DB (use the [link](https://drive.google.com/file/d/1nGDtBZTlKwpituH9trawr0QZXLh7HdMI/view) to download it)

Run in the terminal to set up DB (make sure to be in the correct folder):
```bash
docker compose build
docker compose up
```

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
pip3 install -r requirements.txt
```

---
