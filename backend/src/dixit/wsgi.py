import eventlet

eventlet.monkey_patch()

from dixit.api import create_app  # noqa: E402

app = create_app()
