from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import Index

# Auto-generated models using Flask-SQLAlchemy
class Manifest(db.Model):
    __tablename__ = 'manifest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    bill_of_lading = db.Column(db.String(255), unique=True)
    shipper_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    consignee_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    vessel_id = db.Column(db.Integer, db.ForeignKey("vessel.id"))
    voyage_id = db.Column(db.Integer, db.ForeignKey("voyage.id"))
    port_of_loading_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    port_of_discharge_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    place_of_delivery = db.Column(db.String(255))
    place_of_receipt = db.Column(db.String(255))
    clauses = db.Column(db.String(255))
    date_of_receipt = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    __table_args__ = (
        Index('ix_manifest_shipper_id', 'shipper_id'),
        Index('ix_manifest_consignee_id', 'consignee_id'),
        Index('ix_manifest_vessel_id', 'vessel_id'),
        Index('ix_manifest_voyage_id', 'voyage_id'),
        Index('ix_manifest_port_of_loading_id', 'port_of_loading_id'),
        Index('ix_manifest_port_of_discharge_id', 'port_of_discharge_id'),
        Index('ix_manifest_user_id', 'user_id'),
    )

    shipper = db.relationship('Client', back_populates='manifest_as_shippers', foreign_keys=[shipper_id])
    consignee = db.relationship('Client', back_populates='manifest_as_consignees', foreign_keys=[consignee_id])
    vessel = db.relationship('Vessel', back_populates='manifests', foreign_keys=[vessel_id])
    voyage = db.relationship('Voyage', back_populates='manifests', foreign_keys=[voyage_id])
    port_of_loading = db.relationship('Port', back_populates='manifest_as_port_of_loadings', foreign_keys=[port_of_loading_id])
    port_of_discharge = db.relationship('Port', back_populates='manifest_as_port_of_discharges', foreign_keys=[port_of_discharge_id])
    user = db.relationship('User', back_populates='manifests', foreign_keys=[user_id])
    line_items = db.relationship('LineItem', back_populates='manifest', primaryjoin='LineItem.manifest_id == Manifest.id', lazy='dynamic')


class LineItem(db.Model):
    __tablename__ = 'lineitem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    manifest_id = db.Column(db.Integer, db.ForeignKey("manifest.id"))
    description = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    pack_type_id = db.Column(db.Integer, db.ForeignKey("packtype.id"))
    commodity_id = db.Column(db.Integer, db.ForeignKey("commodity.id"))
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    __table_args__ = (
        Index('ix_lineitem_manifest_id', 'manifest_id'),
        Index('ix_lineitem_pack_type_id', 'pack_type_id'),
        Index('ix_lineitem_commodity_id', 'commodity_id'),
        Index('ix_lineitem_container_id', 'container_id'),
        Index('ix_lineitem_user_id', 'user_id'),
    )

    manifest = db.relationship('Manifest', back_populates='line_items', foreign_keys=[manifest_id])
    pack_type = db.relationship('PackType', back_populates='line_items', foreign_keys=[pack_type_id])
    commodity = db.relationship('Commodity', back_populates='line_items', foreign_keys=[commodity_id])
    container = db.relationship('Container', back_populates='line_items', foreign_keys=[container_id])
    user = db.relationship('User', back_populates='line_items', foreign_keys=[user_id])


class Commodity(db.Model):
    __tablename__ = 'commodity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('LineItem', back_populates='commodity', primaryjoin='LineItem.commodity_id == Commodity.id', lazy='dynamic')
    rates = db.relationship('Rate', back_populates='commodity', primaryjoin='Rate.commodity_id == Commodity.id', lazy='dynamic')


class PackType(db.Model):
    __tablename__ = 'packtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('LineItem', back_populates='pack_type', primaryjoin='LineItem.pack_type_id == PackType.id', lazy='dynamic')
    rates = db.relationship('Rate', back_populates='pack_type', primaryjoin='Rate.pack_type_id == PackType.id', lazy='dynamic')


class Container(db.Model):
    __tablename__ = 'container'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    number = db.Column(db.String(255), unique=True)
    port_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_container_port_id', 'port_id'),
    )

    line_items = db.relationship('LineItem', back_populates='container', primaryjoin='LineItem.container_id == Container.id', lazy='dynamic')
    port = db.relationship('Port', back_populates='containers', foreign_keys=[port_id])
    container_histories = db.relationship('ContainerHistory', back_populates='container', primaryjoin='ContainerHistory.container_id == Container.id', lazy='dynamic')


class ContainerHistory(db.Model):
    __tablename__ = 'containerhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    port_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    container_status_id = db.Column(db.Integer, db.ForeignKey("containerstatus.id"))
    damage = db.Column(db.String(255))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_containerhistory_container_id', 'container_id'),
        Index('ix_containerhistory_port_id', 'port_id'),
        Index('ix_containerhistory_client_id', 'client_id'),
        Index('ix_containerhistory_container_status_id', 'container_status_id'),
    )

    container = db.relationship('Container', back_populates='container_histories', foreign_keys=[container_id])
    port = db.relationship('Port', back_populates='container_histories', foreign_keys=[port_id])
    client = db.relationship('Client', back_populates='container_histories', foreign_keys=[client_id])
    container_status = db.relationship('ContainerStatus', back_populates='container_histories', foreign_keys=[container_status_id])


class ContainerStatus(db.Model):
    __tablename__ = 'containerstatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    container_histories = db.relationship('ContainerHistory', back_populates='container_status', primaryjoin='ContainerHistory.container_status_id == ContainerStatus.id', lazy='dynamic')


class ShippingCompany(db.Model):
    __tablename__ = 'shippingcompany'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    vessels = db.relationship('Vessel', back_populates='shipping_company', primaryjoin='Vessel.shipping_company_id == ShippingCompany.id', lazy='dynamic')


class Vessel(db.Model):
    __tablename__ = 'vessel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    shipping_company_id = db.Column(db.Integer, db.ForeignKey("shippingcompany.id"))

    __table_args__ = (
        Index('ix_vessel_shipping_company_id', 'shipping_company_id'),
    )

    manifests = db.relationship('Manifest', back_populates='vessel', primaryjoin='Manifest.vessel_id == Vessel.id', lazy='dynamic')
    shipping_company = db.relationship('ShippingCompany', back_populates='vessels', foreign_keys=[shipping_company_id])
    voyages = db.relationship('Voyage', back_populates='vessel', primaryjoin='Voyage.vessel_id == Vessel.id', lazy='dynamic')


class Voyage(db.Model):
    __tablename__ = 'voyage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey("vessel.id"))
    rotation_number = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_voyage_vessel_id', 'vessel_id'),
    )

    manifests = db.relationship('Manifest', back_populates='voyage', primaryjoin='Manifest.voyage_id == Voyage.id', lazy='dynamic')
    vessel = db.relationship('Vessel', back_populates='voyages', foreign_keys=[vessel_id])
    legs = db.relationship('Leg', back_populates='voyage', primaryjoin='Leg.voyage_id == Voyage.id', lazy='dynamic')


class Leg(db.Model):
    __tablename__ = 'leg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    voyage_id = db.Column(db.Integer, db.ForeignKey("voyage.id"))
    port_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    leg_number = db.Column(db.Integer)
    eta = db.Column(db.DateTime)
    etd = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_leg_voyage_id', 'voyage_id'),
        Index('ix_leg_port_id', 'port_id'),
    )

    voyage = db.relationship('Voyage', back_populates='legs', foreign_keys=[voyage_id])
    port = db.relationship('Port', back_populates='legs', foreign_keys=[port_id])


class Port(db.Model):
    __tablename__ = 'port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    prefix = db.Column(db.String(255))

    __table_args__ = (
        Index('ix_port_country_id', 'country_id'),
    )

    manifest_as_port_of_loadings = db.relationship('Manifest', back_populates='port_of_loading', primaryjoin='Manifest.port_of_loading_id == Port.id', lazy='dynamic')
    manifest_as_port_of_discharges = db.relationship('Manifest', back_populates='port_of_discharge', primaryjoin='Manifest.port_of_discharge_id == Port.id', lazy='dynamic')
    containers = db.relationship('Container', back_populates='port', primaryjoin='Container.port_id == Port.id', lazy='dynamic')
    container_histories = db.relationship('ContainerHistory', back_populates='port', primaryjoin='ContainerHistory.port_id == Port.id', lazy='dynamic')
    legs = db.relationship('Leg', back_populates='port', primaryjoin='Leg.port_id == Port.id', lazy='dynamic')
    country = db.relationship('Country', back_populates='ports', foreign_keys=[country_id])
    port_pair_as_pols = db.relationship('PortPair', back_populates='pol', primaryjoin='PortPair.pol_id == Port.id', lazy='dynamic')
    port_pair_as_pods = db.relationship('PortPair', back_populates='pod', primaryjoin='PortPair.pod_id == Port.id', lazy='dynamic')


class PortPair(db.Model):
    __tablename__ = 'portpair'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    pol_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    pod_id = db.Column(db.Integer, db.ForeignKey("port.id"))
    distance = db.Column(db.Integer)
    distance_rate_code = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_portpair_pol_id', 'pol_id'),
        Index('ix_portpair_pod_id', 'pod_id'),
    )

    pol = db.relationship('Port', back_populates='port_pair_as_pols', foreign_keys=[pol_id])
    pod = db.relationship('Port', back_populates='port_pair_as_pods', foreign_keys=[pod_id])


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    ports = db.relationship('Port', back_populates='country', primaryjoin='Port.country_id == Country.id', lazy='dynamic')
    clients = db.relationship('Client', back_populates='country', primaryjoin='Client.country_id == Country.id', lazy='dynamic')


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    address = db.Column(db.String(255))
    town = db.Column(db.String(255))
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    contact_person = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))

    __table_args__ = (
        Index('ix_client_country_id', 'country_id'),
    )

    manifest_as_shippers = db.relationship('Manifest', back_populates='shipper', primaryjoin='Manifest.shipper_id == Client.id', lazy='dynamic')
    manifest_as_consignees = db.relationship('Manifest', back_populates='consignee', primaryjoin='Manifest.consignee_id == Client.id', lazy='dynamic')
    container_histories = db.relationship('ContainerHistory', back_populates='client', primaryjoin='ContainerHistory.client_id == Client.id', lazy='dynamic')
    country = db.relationship('Country', back_populates='clients', foreign_keys=[country_id])
    rates = db.relationship('Rate', back_populates='client', primaryjoin='Rate.client_id == Client.id', lazy='dynamic')


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))

    manifests = db.relationship('Manifest', back_populates='user', primaryjoin='Manifest.user_id == User.id', lazy='dynamic')
    line_items = db.relationship('LineItem', back_populates='user', primaryjoin='LineItem.user_id == User.id', lazy='dynamic')


class Rate(db.Model):
    __tablename__ = 'rate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    distance_rate_code = db.Column(db.Integer)
    commodity_id = db.Column(db.Integer, db.ForeignKey("commodity.id"))
    pack_type_id = db.Column(db.Integer, db.ForeignKey("packtype.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    rate = db.Column(db.Float)
    effective = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_rate_commodity_id', 'commodity_id'),
        Index('ix_rate_pack_type_id', 'pack_type_id'),
        Index('ix_rate_client_id', 'client_id'),
    )

    commodity = db.relationship('Commodity', back_populates='rates', foreign_keys=[commodity_id])
    pack_type = db.relationship('PackType', back_populates='rates', foreign_keys=[pack_type_id])
    client = db.relationship('Client', back_populates='rates', foreign_keys=[client_id])
