import os
import tempfile
import uuid


# Keep automated tests isolated from the application's real SQLite database.
os.environ.setdefault("DENGUE_DB_PATH", os.path.join(tempfile.gettempdir(), f"dengue-test-{uuid.uuid4().hex}.db"))
