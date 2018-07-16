from flask import Blueprint

blueprint = Blueprint('api', __name__, url_prefix='/api',)


from config import CONTRACT_ADDRESS, START_BLOCK

@blueprint.route('/', methods=['GET'])
def index():
    """Index page."""
    return 'Tokenscan {} {}'.format(CONTRACT_ADDRESS, START_BLOCK)
