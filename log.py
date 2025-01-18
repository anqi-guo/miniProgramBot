import logging

def setup_logging(log_file="hospital_mini_program.log"):
    """
    Configures logging for the application.

    :param log_file: The name of the file to log messages to (default: "hospital_mini_program.log").
    """
    # Check if the logger already has handlers to prevent duplicates
    logger = logging.getLogger()
    if not logger.handlers:
        # Configure logging to a file
        logging.basicConfig(
            level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename=log_file,  # Logs to the specified file
            filemode="a"  # Append mode; use "w" to overwrite the log file each time
        )

        # Add a console handler to also log messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(console_handler)