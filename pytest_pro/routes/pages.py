"""HTML sayfaları."""
from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.route("/")
def student_page():
    return render_template("index.html")


@bp.route("/pratik")
def practice_page():
    return render_template("practice.html")


@bp.route("/ogretmen")
def teacher_page():
    return render_template("teacher.html")
