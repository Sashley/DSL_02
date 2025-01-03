from app import db
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import Index

# Auto-generated models using Flask-SQLAlchemy
class S001_Manifest(db.Model):
    __tablename__ = 's001_manifest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    bill_of_lading = db.Column(db.String(255), unique=True)
    shipper_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    consignee_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    vessel_id = db.Column(db.Integer, db.ForeignKey("s009_vessel.id"))
    voyage_id = db.Column(db.Integer, db.ForeignKey("s010_voyage.id"))
    port_of_loading_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    port_of_discharge_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    place_of_delivery = db.Column(db.String(255))
    place_of_receipt = db.Column(db.String(255))
    clauses = db.Column(db.String(255))
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

    line_items = db.relationship('S002_LineItem', back_populates='manifest', lazy='dynamic')
    shipper = db.relationship('S015_Client', foreign_keys=[shipper_id], back_populates='manifests')
    consignee = db.relationship('S015_Client', foreign_keys=[consignee_id], back_populates='consigned_manifests')
    vessel = db.relationship('S009_Vessel', foreign_keys=[vessel_id], back_populates='manifests')
    voyage = db.relationship('S010_Voyage', foreign_keys=[voyage_id], back_populates='manifests')
    port_of_loading = db.relationship('S012_Port', foreign_keys=[port_of_loading_id], back_populates=None)
    port_of_discharge = db.relationship('S012_Port', foreign_keys=[port_of_discharge_id], back_populates=None)
    user = db.relationship('S016_User', foreign_keys=[user_id], back_populates=None)


class S002_LineItem(db.Model):
    __tablename__ = 's002_lineitem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    manifest_id = db.Column(db.Integer, db.ForeignKey("s001_manifest.id"))
    description = db.Column(db.String(255))
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

    manifest = db.relationship('S001_Manifest', foreign_keys=[manifest_id], back_populates='line_items')
    pack_type = db.relationship('S004_PackType', foreign_keys=[pack_type_id], back_populates='line_items')
    commodity = db.relationship('S003_Commodity', foreign_keys=[commodity_id], back_populates='line_items')
    container = db.relationship('S005_Container', foreign_keys=[container_id], back_populates='line_items')
    user = db.relationship('S016_User', foreign_keys=[user_id], back_populates=None)


class S003_Commodity(db.Model):
    __tablename__ = 's003_commodity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('S002_LineItem', back_populates='commodity', lazy='dynamic')


class S004_PackType(db.Model):
    __tablename__ = 's004_packtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('S002_LineItem', back_populates='pack_type', lazy='dynamic')


class S005_Container(db.Model):
    __tablename__ = 's005_container'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    number = db.Column(db.String(255), unique=True)
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s005_container_port_id', 'port_id')
    )

    line_items = db.relationship('S002_LineItem', back_populates='container', lazy='dynamic')
    container_histories = db.relationship('S006_ContainerHistory', back_populates='container', lazy='dynamic')
    port = db.relationship('S012_Port', foreign_keys=[port_id], back_populates='containers')


class S006_ContainerHistory(db.Model):
    __tablename__ = 's006_containerhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey("s005_container.id"))
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("s015_client.id"))
    container_status_id = db.Column(db.Integer, db.ForeignKey("s007_containerstatus.id"))
    damage = db.Column(db.String(255))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s006_containerhistory_container_id', 'container_id'),
        Index('ix_s006_containerhistory_port_id', 'port_id'),
        Index('ix_s006_containerhistory_client_id', 'client_id'),
        Index('ix_s006_containerhistory_container_status_id', 'container_status_id')
    )

    container = db.relationship('S005_Container', foreign_keys=[container_id], back_populates='container_histories')
    port = db.relationship('S012_Port', foreign_keys=[port_id], back_populates=None)
    client = db.relationship('S015_Client', foreign_keys=[client_id], back_populates=None)
    container_status = db.relationship('S007_ContainerStatus', foreign_keys=[container_status_id], back_populates='container_histories')


class S007_ContainerStatus(db.Model):
    __tablename__ = 's007_containerstatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    container_histories = db.relationship('S006_ContainerHistory', back_populates='container_status', lazy='dynamic')


class S008_ShippingCompany(db.Model):
    __tablename__ = 's008_shippingcompany'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    vessels = db.relationship('S009_Vessel', back_populates='shipping_company', lazy='dynamic')


class S009_Vessel(db.Model):
    __tablename__ = 's009_vessel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    shipping_company_id = db.Column(db.Integer, db.ForeignKey("s008_shippingcompany.id"))

    __table_args__ = (
        Index('ix_s009_vessel_shipping_company_id', 'shipping_company_id')
    )

    manifests = db.relationship('S001_Manifest', back_populates='vessel', lazy='dynamic')
    shipping_company = db.relationship('S008_ShippingCompany', foreign_keys=[shipping_company_id], back_populates='vessels')


class S010_Voyage(db.Model):
    __tablename__ = 's010_voyage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey("s009_vessel.id"))
    rotation_number = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_s010_voyage_vessel_id', 'vessel_id')
    )

    legs = db.relationship('S011_Leg', back_populates='voyage', lazy='dynamic')
    manifests = db.relationship('S001_Manifest', back_populates='voyage', lazy='dynamic')
    vessel = db.relationship('S009_Vessel', foreign_keys=[vessel_id], back_populates='voyages')


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

    voyage = db.relationship('S010_Voyage', foreign_keys=[voyage_id], back_populates='legs')
    port = db.relationship('S012_Port', foreign_keys=[port_id], back_populates='legs')


class S012_Port(db.Model):
    __tablename__ = 's012_port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("s014_country.id"))
    prefix = db.Column(db.String(255))

    __table_args__ = (
        Index('ix_s012_port_country_id', 'country_id')
    )

    containers = db.relationship('S005_Container', back_populates='port', lazy='dynamic')
    country = db.relationship('S014_Country', foreign_keys=[country_id], back_populates='ports')


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

    port_of_loading = db.relationship('S012_Port', foreign_keys=[pol_id], back_populates='port_of_loading')
    port_of_discharge = db.relationship('S012_Port', foreign_keys=[pod_id], back_populates='port_of_discharge')


class S014_Country(db.Model):
    __tablename__ = 's014_country'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    ports = db.relationship('S012_Port', back_populates='country', lazy='dynamic')


class S015_Client(db.Model):
    __tablename__ = 's015_client'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    town = db.Column(db.String(255))
    country_id = db.Column(db.Integer, db.ForeignKey("s014_country.id"))
    contact_person = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))

    __table_args__ = (
        Index('ix_s015_client_country_id', 'country_id')
    )

    manifests = db.relationship('S001_Manifest', back_populates='shipper', lazy='dynamic')
    consigned_manifests = db.relationship('S001_Manifest', back_populates='consignee', lazy='dynamic')
    country = db.relationship('S014_Country', foreign_keys=[country_id], back_populates='clients')


class S016_User(db.Model):
    __tablename__ = 's016_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))

    manifests = db.relationship('S001_Manifest', back_populates=None, lazy='dynamic')
    line_items = db.relationship('S002_LineItem', back_populates=None, lazy='dynamic')


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

    commodity = db.relationship('S003_Commodity', foreign_keys=[commodity_id], back_populates='rates')
    pack_type = db.relationship('S004_PackType', foreign_keys=[pack_type_id], back_populates='rates')
    client = db.relationship('S015_Client', foreign_keys=[client_id], back_populates='rates')


