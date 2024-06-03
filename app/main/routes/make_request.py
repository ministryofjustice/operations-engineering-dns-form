from flask import (
    Blueprint,
    request,
    current_app,
    render_template,
    flash
)

make_request_route = Blueprint("make_request_route", __name__)

@make_request_route.route("/submit-dns-request", methods = ["POST"])
def submit_dns_request():
    try:
        current_app.github_service.submit_issue(request.form.to_dict())
        return render_template("pages/request-complete.html")
    except:
        flash("Failed to submit request")
