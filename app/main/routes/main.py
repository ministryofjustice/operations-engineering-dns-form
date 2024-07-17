from flask import Blueprint, current_app, redirect, render_template, request, url_for

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("pages/main_form.html")


@main.route("/select-change-type", methods=["POST"])
def select_change_type():
    change_type = request.form["change_type"]
    if change_type == "create_record":
        return redirect("/create-record")
    return redirect("/")


@main.route("/create-record", methods=["GET", "POST"])
def create_record():
    if request.method == "POST":
        form_data = request.form.to_dict()

        full_dns_record = form_data["dns_record"]
        record_name, domain_name = full_dns_record.split(".", 1)

        form_data["record_name"] = record_name
        form_data["domain_name"] = domain_name

        issue = current_app.github_service.submit_issue(form_data)
        pr_link = current_app.github_service.create_pr(form_data, issue)

        return render_template("pages/confirmation.html", pr_url=pr_link)

    return render_template("pages/create_record_form.html")
