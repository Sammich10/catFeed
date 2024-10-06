from app import app
from app.appLocal import catFeedLocalProc
import os
import atexit
import multiprocessing
            
local_process = multiprocessing.Process(target=catFeedLocalProc, daemon=True)
      
if __name__ == "__main__":
    local_process.start()
    print("Started local application process, PID: " + str(local_process.pid))
    atexit.register(lambda: os.kill(local_process.pid, 9))
    app.run(host="0.0.0.0", port = "5000", debug=True)