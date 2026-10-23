# Recallio — Starter App

A responsive Streamlit study app that accepts PDF, DOCX and TXT materials, creates quizzes, scores answers, and links incorrect answers to source passages for revision.

## 1. Requirements

- Python 3.10 or newer (Python 3.11 is a good choice)
- PyCharm
- Internet connection for installing packages and optional Gemini API calls

## 2. Open in PyCharm

1. Extract `Recallio_Starter.zip`.
2. In PyCharm, choose **Open** and select the `Recallio_Starter` folder.
3. Create a virtual environment when PyCharm offers.
4. Open the PyCharm Terminal.

Install packages:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run app.py
```

The terminal will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## 3. Optional AI-generated questions

The app can run without an AI key using a basic source-comprehension fallback. For more varied AI-generated questions:

1. Create an API key through Google AI Studio, subject to Google's current eligibility and terms.
2. For local testing, set an environment variable before running the app.

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="paste-your-key-here"
python -m streamlit run app.py
```

macOS/Linux:

```bash
export GEMINI_API_KEY="paste-your-key-here"
python -m streamlit run app.py
```

You may set `GEMINI_MODEL` to a model available to your account. Model names, free-tier quotas, and terms can change. Never commit a real key to GitHub or put it in frontend code.

## 4. Publish a link

A simple hosting option for a first prototype is Streamlit Community Cloud. Availability, usage limits, and current plan terms may change.

1. Create a GitHub repository for this project.
2. Upload `app.py`, `requirements.txt`, `.streamlit/config.toml`, and this README.
3. Do **not** upload `.env` files or API keys.
4. Sign in to Streamlit Community Cloud and deploy the repository, selecting `app.py` as the entry point.
5. If using Gemini, add `GEMINI_API_KEY` in the app's Secrets settings. Example:

```toml
GEMINI_API_KEY = "your-secret-key"
GEMINI_MODEL = "gemini-2.5-flash"
```

6. Deploy. The host will provide a shareable web link.

## 5. Important limitations of this starter

This is a first prototype, not yet a production multi-user service.

- Uploaded documents, current quiz and history are kept in Streamlit session state; this is not permanent storage.
- The current PDF view links to extracted passages rather than drawing pixel-perfect annotations over the original PDF page.
- Scanned/image-only PDFs need OCR, not included in this starter.
- The fallback question mode is deliberately simple and is not a substitute for an AI model.
- A public multi-user launch should add user accounts, persistent database storage, private file storage, authorization checks, quotas, and a tested source-anchor/highlighting layer.
- Do not upload confidential, personal, or sensitive documents to a public prototype.

## 6. Troubleshooting

**`streamlit` is not recognized**  
Run `python -m streamlit run app.py` instead of `streamlit run app.py`.

**Package installation errors**  
Check that PyCharm's selected interpreter is the project's virtual environment, then run `python -m pip install -r requirements.txt` again.

**AI request fails**  
Check the API key, model name, account eligibility, internet connection, and remaining quota. The app falls back to basic source questions when AI generation is unavailable.

**PDF has no readable text**  
It may be a scanned document. Use a text-selectable PDF or add OCR support later.
