# Movie Recommendation System

This project consists of a Python Flask backend for recommendations and a modern HTML/CSS/JS frontend.

## How to Run Locally

Since this is a Python project, you don't use `npm`. Instead, follow these steps:

1. **Install Dependencies** (if you haven't already):

   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Backend Server**:

   ```bash
   python api/index.py
   ```

   This will start the API server at `http://127.0.0.1:5000`.
3. **Open the Frontend**:

   - Simply open the `public/index.html` file in your browser.
   - OR for a better experience, serve it with Python:
     ```bash
     # On a separate terminal in the Deployment folder
     python -m http.server 8000 --directory public
     ```

     Then open `http://localhost:8000`.

## How to Deploy to Vercel

1. **Install Vercel CLI** (if needed):

   ```bash
   npm i -g vercel
   ```
2. **Deploy**:
   Run this command in the `Deployment` folder:

   ```bash
   vercel
   ```

   Follow the prompts (say 'Yes' to everything, keep defaults).

## Project Structure

- `api/index.py`: The Flask backend.
- `public/`: The frontend files.
- `requirements.txt`: Python libraries.
- `vercel.json`: Deployment configuration.
