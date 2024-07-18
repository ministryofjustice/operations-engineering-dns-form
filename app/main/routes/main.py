from flask import Blueprint, current_app, jsonify, redirect, render_template, request

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
        if "." not in full_dns_record:
            return render_template(
                "pages/create_record_form.html", error="Invalid DNS record format"
            )

        record_name, domain_name = full_dns_record.split(".", 1)

        hosted_zones = current_app.github_service.get_hosted_zones()
        if domain_name not in hosted_zones:
            return render_template(
                "pages/create_record_form.html",
                error=f"Domain {domain_name} does not exist",
            )

        # Update form_data with parsed values
        form_data["record_name"] = record_name
        form_data["domain_name"] = domain_name

        issue = current_app.github_service.submit_issue(form_data)
        pr_link = current_app.github_service.create_pr(form_data, issue)

        return render_template("pages/confirmation.html", pr_url=pr_link)

    return render_template("pages/create_record_form.html")


@main.route("/api/hosted_zones", methods=["GET"])
def get_hosted_zones():
    try:
        hosted_zones = current_app.github_service.get_hosted_zones()
        return jsonify(hosted_zones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
