import logging

from flask import (
    Blueprint,
    request,
    current_app,
    render_template,
    flash
)

logger = logging.getLogger(__name__)
make_request_route = Blueprint("make_request_route", __name__)

@make_request_route.route("/submit-dns-request", methods = ["POST"])
def submit_dns_request():
    data = request.form.to_dict()
    logger.info(data)
    current_app.github_service.submit_issue(data)
    return render_template("pages/request-complete.html")
