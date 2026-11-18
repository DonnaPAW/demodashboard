from flask import Flask, abort, render_template, send_file

from db import company_report, get_companies, overview
from pdf import company_pdf, overview_pdf

app = Flask(__name__)


@app.route("/")
def dashboard():
    data = overview()
    companies = get_companies()
    reports = {c["id"]: company_report(c["id"]) for c in companies}
    total_used = sum(r["points_used"] for r in data["companies"])
    total_contingent = sum(r["points_contingent"] for r in data["companies"])
    return render_template(
        "index.html",
        companies=data["companies"],
        total_events=data["total_events"],
        total_bookings=data["total_bookings"],
        total_used=total_used,
        total_contingent=total_contingent,
        reports=reports,
    )


@app.route("/pdf/overview")
def pdf_overview():
    path = overview_pdf()
    return send_file(path, as_attachment=True, download_name="auswertung_gesamt.pdf")


@app.route("/pdf/company/<int:company_id>")
def pdf_company(company_id):
    report = company_report(company_id)
    if report is None:
        abort(404)
    path = company_pdf(report)
    name = report["company"]["name"].replace(" ", "_").replace("/", "-")
    return send_file(path, as_attachment=True, download_name=f"bericht_{name}.pdf")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
