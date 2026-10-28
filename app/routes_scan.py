from flask import Blueprint, request, jsonify, session, render_template
from app.auth import authenticate_operator
from app.config import Config
from app.scan import finalize_scan, validate_scan

scan_bp = Blueprint("scan", __name__)

# ── Auth ──────────────────────────────────────────────────────────────────────

@scan_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@scan_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    employee_num = (data.get("employee_num") or "").strip()
    if not employee_num:
        return jsonify({"ok": False, "message": "Employee number is required."}), 400

    operator = authenticate_operator(employee_num)
    
    if not operator:
        return jsonify({
            "ok": False,
            "message": "Unable to sign in. Check your employee number and try again.",
        }), 401

    session["operator_en"] = operator["operator_en"]
    session["employee_num"] = employee_num
    return jsonify({"ok": True, "operator_en": operator["operator_en"]})

@scan_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

# ── Scan UI ───────────────────────────────────────────────────────────────────

@scan_bp.route("/")
def index():
    if "operator_en" not in session:
        from flask import redirect, url_for
        return redirect(url_for("scan.login_page"))
    return render_template("scan.html",
                           operator_en=session["operator_en"],
                           tray_limit=Config.TRAY_LIMIT)

# ── Prog ID scan ─────────────────────────────────────────────────────────────

@scan_bp.route("/api/check-prog", methods=["POST"])
def api_check_prog():
    if "operator_en" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    data = request.get_json(force=True)
    prog_id = (data.get("prog_id") or "").strip()

    if not prog_id:
        return jsonify({"ok": False, "message": "Prog ID is required."}), 400

    result = validate_scan(prog_id)
    ok = result["status"] == "ok"
    return jsonify({"ok": ok, **result})

# ── Pass / Fail decision ─────────────────────────────────────────────────────

@scan_bp.route("/api/scan-decision", methods=["POST"])
def api_scan_decision():
    if "operator_en" not in session:
        return jsonify({"ok": False, "message": "Not authenticated."}), 401

    data = request.get_json(force=True)
    prog_id    = (data.get("prog_id") or "").strip()
    decision   = (data.get("decision") or "").strip().lower()
    shift      = (data.get("shift") or "").strip()
    remarks    = (data.get("remarks") or "").strip()

    if not prog_id:
        return jsonify({"ok": False, "message": "Prog ID is required."}), 400
    if decision not in ("pass", "fail"):
        return jsonify({"ok": False, "message": "Decision must be 'pass' or 'fail'."}), 400
    if decision == "fail" and not remarks:
        return jsonify({"ok": False, "message": "Please enter a fail reason."}), 400

    result = finalize_scan(
        prog_id=prog_id,
        operator_en=session["operator_en"],
        shift=shift,
        decision=decision,
        remarks=remarks,
    )

    ok = result["status"] == "ok"
    return jsonify({"ok": ok, **result})