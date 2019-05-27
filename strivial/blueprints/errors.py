from flask import Blueprint, render_template

bp = Blueprint('errors', __name__, url_prefix='/')

'''
displays a custom 500 error page
'''
@bp.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

'''
displays a custom 404 error page
'''
@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404