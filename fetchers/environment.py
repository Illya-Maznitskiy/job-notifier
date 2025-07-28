from utils.convert_bool import str_to_bool
from dotenv import load_dotenv
from os import getenv

is_loaded = False

class Environment:
    """
    This class is for environment variables.
    """
    @staticmethod
    def load_service(service_name: str) -> tuple[str, bool]:
        if not is_loaded:
            load_dotenv()

        return (
            getenv(f"{service_name.upper()}_URL"),
            str_to_bool(getenv(f"{service_name.upper()}_HEADLESS")),
        )

    @staticmethod
    def hard_load():
        global is_loaded

        load_dotenv()

        is_loaded = True