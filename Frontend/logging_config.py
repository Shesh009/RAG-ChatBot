# logging_config.py
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("Frontend_logging.log"),
            logging.StreamHandler()
        ]
    )
