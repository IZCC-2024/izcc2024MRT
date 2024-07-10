import io
import logging
import json
from flask import Blueprint, Response, render_template, redirect, send_file, session 
from zenora import APIClient

from ..core import core

core.create_team("test", ["0"], ["e04._.40e", "a.uuu", "lucasw0"])

log = logging.getLogger(__name__)
main = Blueprint("main", __name__)


@main.after_request
def checking(response: Response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "deny"
    return response
    

@main.route("/")
def index():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, is_admin = core.check_player(current_user.username)
        if is_admin:
            return redirect("/admin")
        else:
            return render_template("index.html", current_user=current_user.username, team=team, graph=core.metro.graph)
    return redirect("/login")


@main.route("/admin")
def admin():
    if "token" in session:
        bearer_client = APIClient(session.get("token"), bearer=True)
        current_user = bearer_client.users.get_current_user()
        team, is_admin = core.check_player(current_user.username)
    
        if is_admin:
            return render_template("admin.html", current_user=current_user.username, team=team, graph=core.metro.graph)
    return redirect("/")


@main.route("/download_graph")
def download_graph():
    with io.StringIO() as file:
        json.dump(core.metro.graph, file, ensure_ascii=False, indent=4)
        response = send_file(file.name, as_attachment=True, download_name="graph.json")
        
    return response