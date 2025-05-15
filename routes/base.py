from flask import Blueprint, render_template

# Define the Blueprint
base_bp = Blueprint('base', __name__, template_folder='templates')

# Route for rendering the base.html
@base_bp.route('/')
def base():
    return render_template('base.html')