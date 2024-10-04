# pylint: disable=C0411

import re

from flask import Blueprint, current_app, flash, redirect, render_template, request

from app.main.middleware.auth import requires_auth
from app.main.validators.index import validate_create_record_form

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("pages/welcome_page.html")


@main.route("/select-change-type", methods=["POST"])
def select_change_type():
    change_type = request.form["change_type"]
    if change_type == "create_record":
        return redirect("/create-record")
    return redirect("/")


@main.route("/create-record", methods=["GET", "POST"])
@requires_auth
def create_record():
    if request.method == "POST":
        form_data = request.form.to_dict()
        errors = validate_create_record_form(form_data)
        if errors:
            for field, error_message in errors.items():
                flash((field, error_message), "form_error")
            return render_template(
                "pages/create_record_form.html", form_data=form_data, errors=errors
            )

        issue_link = current_app.github_service.submit_issue(form_data)

        issue_number = re.search(r"/issues/(\d+)", issue_link)
        if issue_number:
            issue_number = issue_number.group(1)

        return render_template("pages/confirmation.html", issue_number=issue_number)

    return render_template("pages/create_record_form.html")
