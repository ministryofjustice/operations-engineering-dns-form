from flask import Blueprint, current_app, redirect, render_template, request, url_for

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("pages/main_form.html")


@main.route("/select-change-type", methods=["POST"])
def select_change_type():
    change_type = request.form["change_type"]
    if change_type == "new_hostedzone":
        return redirect("/new-hostedzone")
    elif change_type == "change_record":
        return redirect("/change-record")
    elif change_type == "create_record":
        return redirect("/create-record")
    return redirect(url_for("main.index"))


@main.route("/new-hostedzone", methods=["GET", "POST"])
def new_hosted_zone():
    if request.method == "POST":
        form_data = request.form.to_dict()
        return redirect("/")
    return render_template("pages/new_hosted_zone_form.html")


@main.route("/change-record", methods=["GET", "POST"])
def change_record():
    if request.method == "POST":
        form_data = request.form.to_dict()
        return redirect("/")
    return render_template("pages/change_record_form.html")


@main.route("/create-record", methods=["GET", "POST"])
def create_record():
    if request.method == "POST":
        form_data = request.form.to_dict()

        issue = current_app.github_service.submit_issue(form_data)
        pr_link = current_app.github_service.create_pr(form_data, issue)

        return render_template("pages/confirmation.html", pr_url=pr_link)

    return render_template("pages/create_record_form.html")
