import faulthandler

from src.core.app import create_app

faulthandler.enable()

app = create_app()
