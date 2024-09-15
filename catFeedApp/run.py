from appMain.app import app
from appMain.feederControl import initializeClasses

if __name__ == "__main__":
    initializeClasses()
    app.run(host="0.0.0.0", port = "5000", debug=True)
