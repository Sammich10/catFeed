from app import create_app
from app.access.access import initialize_hardware, shutdown_hardware
import os, atexit
from app.configuration import HardwareConfig as hwConfig
    
    
from app.tasks import create_display_task
    
def start_app():
    """
    Starts the Flask app, initializes the hardware if this is the first time the
    app is being run, and registers the shutdown function to be called when the
    app exits.

    Args:
        None

    Returns:
        None
    """
    app = create_app()
    # If this is the first time the app is being run, initialize the hardware
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        initialize_hardware()
        create_display_task(5)
    # Register the shutdown function
    atexit.register(shutdown_hardware)
    app.run(host="0.0.0.0", port = "5000", debug=True)

def main():
    """
    Entry point for the application.

    This function starts the Flask app and configures the display screen
    updates. It initializes the necessary components and ensures that the
    application runs as intended.

    Args:
        None

    Returns:
        None
    """
    start_app()
    
if __name__ == "__main__":
    main()