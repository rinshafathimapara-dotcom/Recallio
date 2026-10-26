# VYRA Studio

VYRA Studio is a Streamlit-based AI video editing prototype that includes:

- Authentication and profile management
- Persistent SQLite-backed project storage
- Media upload flow for photo and video imports
- Template library with 12 original presets
- New creation workspace with prompt-driven editing ideas
- Editable draft workspace and conversational AI revision flow
- Render workflow UI with a clear integration placeholder for real media engines

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- This build is intentionally honest about render capability: it includes a real workflow, status tracking, and integration hook, but does not pretend a production video export exists without a connected renderer.
- User data and project records are stored in a local SQLite database (`vyra.db`) created automatically when the app runs.
