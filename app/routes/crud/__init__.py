from flask import Blueprint

bp = Blueprint('crud', __name__)

from app.routes.crud import s001_manifest
bp.register_blueprint(s001_manifest.bp, url_prefix='/s001_manifest')

from app.routes.crud import s002_lineitem
bp.register_blueprint(s002_lineitem.bp, url_prefix='/s002_lineitem')

from app.routes.crud import s003_commodity
bp.register_blueprint(s003_commodity.bp, url_prefix='/s003_commodity')

from app.routes.crud import s004_packtype
bp.register_blueprint(s004_packtype.bp, url_prefix='/s004_packtype')

from app.routes.crud import s005_container
bp.register_blueprint(s005_container.bp, url_prefix='/s005_container')

from app.routes.crud import s006_containerhistory
bp.register_blueprint(s006_containerhistory.bp, url_prefix='/s006_containerhistory')

from app.routes.crud import s007_containerstatus
bp.register_blueprint(s007_containerstatus.bp, url_prefix='/s007_containerstatus')

from app.routes.crud import s008_shippingcompany
bp.register_blueprint(s008_shippingcompany.bp, url_prefix='/s008_shippingcompany')

from app.routes.crud import s009_vessel
bp.register_blueprint(s009_vessel.bp, url_prefix='/s009_vessel')

from app.routes.crud import s010_voyage
bp.register_blueprint(s010_voyage.bp, url_prefix='/s010_voyage')

from app.routes.crud import s011_leg
bp.register_blueprint(s011_leg.bp, url_prefix='/s011_leg')

from app.routes.crud import s012_port
bp.register_blueprint(s012_port.bp, url_prefix='/s012_port')

from app.routes.crud import s013_portpair
bp.register_blueprint(s013_portpair.bp, url_prefix='/s013_portpair')

from app.routes.crud import s014_country
bp.register_blueprint(s014_country.bp, url_prefix='/s014_country')

from app.routes.crud import s015_client
bp.register_blueprint(s015_client.bp, url_prefix='/s015_client')

from app.routes.crud import s016_user
bp.register_blueprint(s016_user.bp, url_prefix='/s016_user')

from app.routes.crud import s017_rate
bp.register_blueprint(s017_rate.bp, url_prefix='/s017_rate')

