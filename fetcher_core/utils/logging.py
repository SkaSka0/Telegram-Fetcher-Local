import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("fetcher_core")

logger = setup_logger() 
