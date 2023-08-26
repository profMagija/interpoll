from .router import app

import sys

app.run(
    debug="debug" in sys.argv,
    load_dotenv=True,
)
