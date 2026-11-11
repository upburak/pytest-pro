"""HTTP rotaları. Her alan kendi Blueprint'ine sahiptir."""
from .pages import bp as pages_bp
from .practice import bp as practice_bp
from .student import bp as student_bp
from .teacher import bp as teacher_bp

BLUEPRINTS = (pages_bp, student_bp, teacher_bp, practice_bp)
