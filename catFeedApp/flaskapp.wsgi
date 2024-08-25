import sys
import logging

sys.path.insert(0,'/home/sampi/catFeedApp/run')

from flaskapp import app as application

# Configure logging
logging.basicConfig(stream=sys.stderr)
application.logger.setLevel(logging.INFO)