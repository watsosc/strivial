from flask import Blueprint, render_template

bp = Blueprint('errors', __name__, url_prefix='/')

# Error handlers.

@bp.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404