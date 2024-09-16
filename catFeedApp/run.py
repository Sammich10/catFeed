from appMain.app import app
from appMain.feederControl import initializeClasses, cleanupClasses
from appMain import routes
from appMain import update
import atexit

if __name__ == "__main__":
    initializeClasses()
    atexit.register(cleanupClasses)
    app.run(host="0.0.0.0", port = "5000", debug=True)
