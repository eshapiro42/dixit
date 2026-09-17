from gevent import monkey

monkey.patch_all()

from dixit.api import create_app  # noqa: E402

app = create_app()
