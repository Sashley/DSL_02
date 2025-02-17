from flask import Blueprint

bp = Blueprint('crud', __name__)

from app.routes.crud import manifest
bp.register_blueprint(manifest.bp, url_prefix='/manifest')

from app.routes.crud import lineitem
bp.register_blueprint(lineitem.bp, url_prefix='/lineitem')

from app.routes.crud import commodity
bp.register_blueprint(commodity.bp, url_prefix='/commodity')

from app.routes.crud import packtype
bp.register_blueprint(packtype.bp, url_prefix='/packtype')

from app.routes.crud import container
bp.register_blueprint(container.bp, url_prefix='/container')

from app.routes.crud import containerhistory
bp.register_blueprint(containerhistory.bp, url_prefix='/containerhistory')

from app.routes.crud import containerstatus
bp.register_blueprint(containerstatus.bp, url_prefix='/containerstatus')

from app.routes.crud import shippingcompany
bp.register_blueprint(shippingcompany.bp, url_prefix='/shippingcompany')

from app.routes.crud import vessel
bp.register_blueprint(vessel.bp, url_prefix='/vessel')

from app.routes.crud import voyage
bp.register_blueprint(voyage.bp, url_prefix='/voyage')

from app.routes.crud import leg
bp.register_blueprint(leg.bp, url_prefix='/leg')

from app.routes.crud import port
bp.register_blueprint(port.bp, url_prefix='/port')

from app.routes.crud import portpair
bp.register_blueprint(portpair.bp, url_prefix='/portpair')

from app.routes.crud import country
bp.register_blueprint(country.bp, url_prefix='/country')

from app.routes.crud import client
bp.register_blueprint(client.bp, url_prefix='/client')

from app.routes.crud import user
bp.register_blueprint(user.bp, url_prefix='/user')

from app.routes.crud import rate
bp.register_blueprint(rate.bp, url_prefix='/rate')

