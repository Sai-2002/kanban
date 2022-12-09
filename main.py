from routes import app
from routes.scheduler import Scheduled
import threading


if __name__ == "__main__":
    app.run(debug=True)
    t1 = threading.Thread(target=Scheduled)
    t1.start()
    