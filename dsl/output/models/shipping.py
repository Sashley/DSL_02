from app import db
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import Index

# Auto-generated models using Flask-SQLAlchemy
class S001_Manifest(db.Model):
    __tablename__ = 's001_manifest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    bill_of_lading = db.Column(db.String(40), unique=True)
    shipper_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    consignee_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    vessel_id = db.Column(db.Integer, db.ForeignKey("s009_vessel.id"))
    voyage_id = db.Column(db.Integer, db.ForeignKey("s010_voyage.id"))
    port_of_loading_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    port_of_discharge_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    place_of_delivery = db.Column(db.String(40))
    place_of_receipt = db.Column(db.String(40))
    clauses = db.Column(db.String(40))
    date_of_receipt = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("s016_user.id"))

    __table_args__ = (
        Index('ix_s001_manifest_shipper_id', 'shipper_id'),
        Index('ix_s001_manifest_consignee_id', 'consignee_id'),
        Index('ix_s001_manifest_vessel_id', 'vessel_id'),
        Index('ix_s001_manifest_voyage_id', 'voyage_id'),
        Index('ix_s001_manifest_port_of_loading_id', 'port_of_loading_id'),
        Index('ix_s001_manifest_port_of_discharge_id', 'port_of_discharge_id'),
        Index('ix_s001_manifest_user_id', 'user_id')
    )

    line_items = db.relationship('S002_LineItem', backref='s001_manifest_line_items', lazy='dynamic')
    shipper = db.relationship('S015_Client', foreign_keys=[shipper_id], backref='s001_manifest_shipper')
    consignee = db.relationship('S015_Client', foreign_keys=[consignee_id], backref='s001_manifest_consignee')
    vessel = db.relationship('S009_Vessel', foreign_keys=[vessel_id], backref='s001_manifest_vessel')
    voyage = db.relationship('S010_Voyage', foreign_keys=[voyage_id], backref='s001_manifest_voyage')
    port_of_loading = db.relationship('S012_Port', foreign_keys=[port_of_loading_id], backref='s001_manifest_port_of_loading')
    port_of_discharge = db.relationship('S012_Port', foreign_keys=[port_of_discharge_id], backref='s001_manifest_port_of_discharge')
    user = db.relationship('S016_User', foreign_keys=[user_id], backref='s001_manifest_user')


class S002_LineItem(db.Model):
    __tablename__ = 's002_lineitem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    manifest_id = db.Column(db.Integer, db.ForeignKey("s001_manifest.id"))
    description = db.Column(db.String(40))
    quantity = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    pack_type_id = db.Column(db.Integer, db.ForeignKey("s004_packtype.id"))
    commodity_id = db.Column(db.Integer, db.ForeignKey("s003_commodity.id"))
    container_id = db.Column(db.Integer, db.ForeignKey("s005_container.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("s016_user.id"))

    __table_args__ = (
        Index('ix_s002_lineitem_manifest_id', 'manifest_id'),
        Index('ix_s002_lineitem_pack_type_id', 'pack_type_id'),
        Index('ix_s002_lineitem_commodity_id', 'commodity_id'),
        Index('ix_s002_lineitem_container_id', 'container_id'),
        Index('ix_s002_lineitem_user_id', 'user_id')
    )

    manifest = db.relationship('S001_Manifest', foreign_keys=[manifest_id], backref='s002_lineitem_manifest')
    pack_type = db.relationship('S004_PackType', foreign_keys=[pack_type_id], backref='s002_lineitem_pack_type')
    commodity = db.relationship('S003_Commodity', foreign_keys=[commodity_id], backref='s002_lineitem_commodity')
    container = db.relationship('S005_Container', foreign_keys=[container_id], backref='s002_lineitem_container')
    user = db.relationship('S016_User', foreign_keys=[user_id], backref='s002_lineitem_user')


class S003_Commodity(db.Model):
    __tablename__ = 's003_commodity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    description = db.Column(db.String(40))

    line_items = db.relationship('S002_LineItem', backref='s003_commodity_line_items', lazy='dynamic')


class S004_PackType(db.Model):
    __tablename__ = 's004_packtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    description = db.Column(db.String(40))

    line_items = db.relationship('S002_LineItem', backref='s004_packtype_line_items', lazy='dynamic')


class S005_Container(db.Model):
    __tablename__ = 's005_container'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    number = db.Column(db.String(40), unique=True)
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s005_container_port_id', 'port_id')
    )

    line_items = db.relationship('S002_LineItem', backref='s005_container_line_items', lazy='dynamic')
    container_histories = db.relationship('S006_ContainerHistory', backref='s005_container_container_histories', lazy='dynamic')
    port = db.relationship('S012_Port', foreign_keys=[port_id], backref='s005_container_port')


class S006_ContainerHistory(db.Model):
    __tablename__ = 's006_containerhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey("s005_container.id"))
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    container_status_id = db.Column(db.Integer, db.ForeignKey("s007_containerstatus.id"))
    damage = db.Column(db.String(40))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s006_containerhistory_container_id', 'container_id'),
        Index('ix_s006_containerhistory_port_id', 'port_id'),
        Index('ix_s006_containerhistory_client_id', 'client_id'),
        Index('ix_s006_containerhistory_container_status_id', 'container_status_id')
    )

    container = db.relationship('S005_Container', foreign_keys=[container_id], backref='s006_containerhistory_container')
    port = db.relationship('S012_Port', foreign_keys=[port_id], backref='s006_containerhistory_port')
    client = db.relationship('S015_Client', foreign_keys=[client_id], backref='s006_containerhistory_client')
    container_status = db.relationship('S007_ContainerStatus', foreign_keys=[container_status_id], backref='s006_containerhistory_container_status')


class S007_ContainerStatus(db.Model):
    __tablename__ = 's007_containerstatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40))
    description = db.Column(db.String(40))

    container_histories = db.relationship('S006_ContainerHistory', backref='s007_containerstatus_container_histories', lazy='dynamic')


class S008_ShippingCompany(db.Model):
    __tablename__ = 's008_shippingcompany'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)

    vessels = db.relationship('S009_Vessel', backref='s008_shippingcompany_vessels', lazy='dynamic')


class S009_Vessel(db.Model):
    __tablename__ = 's009_vessel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40))
    shipping_company_id = db.Column(db.Integer, db.ForeignKey("s008_shippingcompany.id"))

    __table_args__ = (
        Index('ix_s009_vessel_shipping_company_id', 'shipping_company_id')
    )

    manifests = db.relationship('S001_Manifest', backref='s009_vessel_manifests', lazy='dynamic')
    shipping_company = db.relationship('S008_ShippingCompany', foreign_keys=[shipping_company_id], backref='s009_vessel_shipping_company')


class S010_Voyage(db.Model):
    __tablename__ = 's010_voyage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey("s009_vessel.id"))
    rotation_number = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_s010_voyage_vessel_id', 'vessel_id')
    )

    legs = db.relationship('S011_Leg', backref='s010_voyage_legs', lazy='dynamic')
    manifests = db.relationship('S001_Manifest', backref='s010_voyage_manifests', lazy='dynamic')
    vessel = db.relationship('S009_Vessel', foreign_keys=[vessel_id], backref='s010_voyage_vessel')


class S011_Leg(db.Model):
    __tablename__ = 's011_leg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    voyage_id = db.Column(db.Integer, db.ForeignKey("s010_voyage.id"))
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    leg_number = db.Column(db.Integer)
    eta = db.Column(db.DateTime)
    etd = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s011_leg_voyage_id', 'voyage_id'),
        Index('ix_s011_leg_port_id', 'port_id')
    )

    voyage = db.relationship('S010_Voyage', foreign_keys=[voyage_id], backref='s011_leg_voyage')
    port = db.relationship('S012_Port', foreign_keys=[port_id], backref='s011_leg_port')


class S012_Port(db.Model):
    __tablename__ = 's012_port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("s014_country.id"))
    prefix = db.Column(db.String(40))

    __table_args__ = (
        Index('ix_s012_port_country_id', 'country_id')
    )

    containers = db.relationship('S005_Container', backref='s012_port_containers', lazy='dynamic')
    country = db.relationship('S014_Country', foreign_keys=[country_id], backref='s012_port_country')


class S013_PortPair(db.Model):
    __tablename__ = 's013_portpair'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    pol_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    pod_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    distance = db.Column(db.Integer)
    distance_rate_code = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_s013_portpair_pol_id', 'pol_id'),
        Index('ix_s013_portpair_pod_id', 'pod_id')
    )

    port_of_loading = db.relationship('S012_Port', foreign_keys=[pol_id], backref='s013_portpair_port_of_loading')
    port_of_discharge = db.relationship('S012_Port', foreign_keys=[pod_id], backref='s013_portpair_port_of_discharge')


class S014_Country(db.Model):
    __tablename__ = 's014_country'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)

    ports = db.relationship('S012_Port', backref='s014_country_ports', lazy='dynamic')


class S015_Client(db.Model):
    __tablename__ = 's015_client'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    address = db.Column(db.String(40))
    town = db.Column(db.String(40))
    country_id = db.Column(db.Integer, db.ForeignKey("s014_country.id"))
    contact_person = db.Column(db.String(40))
    email = db.Column(db.String(40))
    phone = db.Column(db.String(40))

    __table_args__ = (
        Index('ix_s015_client_country_id', 'country_id')
    )

    manifests = db.relationship('S001_Manifest', backref='s015_client_manifests', lazy='dynamic')
    consigned_manifests = db.relationship('S001_Manifest', backref='s015_client_consigned_manifests', lazy='dynamic')
    country = db.relationship('S014_Country', foreign_keys=[country_id], backref='s015_client_country')


class S016_User(db.Model):
    __tablename__ = 's016_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(40))
    password_hash = db.Column(db.String(40))

    manifests = db.relationship('S001_Manifest', backref='s016_user_manifests', lazy='dynamic')
    line_items = db.relationship('S002_LineItem', backref='s016_user_line_items', lazy='dynamic')


class S017_Rate(db.Model):
    __tablename__ = 's017_rate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    distance_rate_code = db.Column(db.Integer)
    commodity_id = db.Column(db.Integer, db.ForeignKey("s003_commodity.id"))
    pack_type_id = db.Column(db.Integer, db.ForeignKey("s004_packtype.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    rate = db.Column(db.Float)
    effective = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s017_rate_commodity_id', 'commodity_id'),
        Index('ix_s017_rate_pack_type_id', 'pack_type_id'),
        Index('ix_s017_rate_client_id', 'client_id')
    )

    commodity = db.relationship('S003_Commodity', foreign_keys=[commodity_id], backref='s017_rate_commodity')
    pack_type = db.relationship('S004_PackType', foreign_keys=[pack_type_id], backref='s017_rate_pack_type')
    client = db.relationship('S015_Client', foreign_keys=[client_id], backref='s017_rate_client')


