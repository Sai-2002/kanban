from routes import app, version
from routes.user_action import token_required

@app.route(f"{version}/")
@token_required
def home(u_id):
    print(f"{u_id}")
    return "<h1>HOME</h1>"