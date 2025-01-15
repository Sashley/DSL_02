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
        Index('ix_s001_manifest_user_id', 'user_id'),
    )

    shipper = db.relationship('S015_Client', back_populates='manifest_as_shippers', foreign_keys=[shipper_id])
    consignee = db.relationship('S015_Client', back_populates='manifest_as_consignees', foreign_keys=[consignee_id])
    vessel = db.relationship('S009_Vessel', back_populates='manifests', foreign_keys=[vessel_id])
    voyage = db.relationship('S010_Voyage', back_populates='manifests', foreign_keys=[voyage_id])
    port_of_loading = db.relationship('S012_Port', back_populates='manifest_as_port_of_loadings', foreign_keys=[port_of_loading_id])
    port_of_discharge = db.relationship('S012_Port', back_populates='manifest_as_port_of_discharges', foreign_keys=[port_of_discharge_id])
    user = db.relationship('S016_User', back_populates='manifests', foreign_keys=[user_id])
    line_items = db.relationship('S002_LineItem', back_populates='manifest', primaryjoin='S002_LineItem.manifest_id == S001_Manifest.id', lazy='dynamic')


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
        Index('ix_s002_lineitem_user_id', 'user_id'),
    )

    manifest = db.relationship('S001_Manifest', back_populates='line_items', foreign_keys=[manifest_id])
    pack_type = db.relationship('S004_PackType', back_populates='line_items', foreign_keys=[pack_type_id])
    commodity = db.relationship('S003_Commodity', back_populates='line_items', foreign_keys=[commodity_id])
    container = db.relationship('S005_Container', back_populates='line_items', foreign_keys=[container_id])
    user = db.relationship('S016_User', back_populates='line_items', foreign_keys=[user_id])


class S003_Commodity(db.Model):
    __tablename__ = 's003_commodity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('S002_LineItem', back_populates='commodity', primaryjoin='S002_LineItem.commodity_id == S003_Commodity.id', lazy='dynamic')
    rates = db.relationship('S017_Rate', back_populates='commodity', primaryjoin='S017_Rate.commodity_id == S003_Commodity.id', lazy='dynamic')


class S004_PackType(db.Model):
    __tablename__ = 's004_packtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    line_items = db.relationship('S002_LineItem', back_populates='pack_type', primaryjoin='S002_LineItem.pack_type_id == S004_PackType.id', lazy='dynamic')
    rates = db.relationship('S017_Rate', back_populates='pack_type', primaryjoin='S017_Rate.pack_type_id == S004_PackType.id', lazy='dynamic')


class S005_Container(db.Model):
    __tablename__ = 's005_container'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    number = db.Column(db.String(255), unique=True)
    port_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    updated = db.Column(db.DateTime)

    __table_args__ = (
        Index('ix_s005_container_port_id', 'port_id'),
    )

    line_items = db.relationship('S002_LineItem', back_populates='container', primaryjoin='S002_LineItem.container_id == S005_Container.id', lazy='dynamic')
    port = db.relationship('S012_Port', back_populates='containers', foreign_keys=[port_id])
    container_histories = db.relationship('S006_ContainerHistory', back_populates='container', primaryjoin='S006_ContainerHistory.container_id == S005_Container.id', lazy='dynamic')


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
        Index('ix_s006_containerhistory_container_status_id', 'container_status_id'),
    )

    container = db.relationship('S005_Container', back_populates='container_histories', foreign_keys=[container_id])
    port = db.relationship('S012_Port', back_populates='container_histories', foreign_keys=[port_id])
    client = db.relationship('S015_Client', back_populates='container_histories', foreign_keys=[client_id])
    container_status = db.relationship('S007_ContainerStatus', back_populates='container_histories', foreign_keys=[container_status_id])


class S007_ContainerStatus(db.Model):
    __tablename__ = 's007_containerstatus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))

    container_histories = db.relationship('S006_ContainerHistory', back_populates='container_status', primaryjoin='S006_ContainerHistory.container_status_id == S007_ContainerStatus.id', lazy='dynamic')


class S008_ShippingCompany(db.Model):
    __tablename__ = 's008_shippingcompany'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    vessels = db.relationship('S009_Vessel', back_populates='shipping_company', primaryjoin='S009_Vessel.shipping_company_id == S008_ShippingCompany.id', lazy='dynamic')


class S009_Vessel(db.Model):
    __tablename__ = 's009_vessel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255))
    shipping_company_id = db.Column(db.Integer, db.ForeignKey("s008_shippingcompany.id"))

    __table_args__ = (
        Index('ix_s009_vessel_shipping_company_id', 'shipping_company_id'),
    )

    manifests = db.relationship('S001_Manifest', back_populates='vessel', primaryjoin='S001_Manifest.vessel_id == S009_Vessel.id', lazy='dynamic')
    shipping_company = db.relationship('S008_ShippingCompany', back_populates='vessels', foreign_keys=[shipping_company_id])
    voyages = db.relationship('S010_Voyage', back_populates='vessel', primaryjoin='S010_Voyage.vessel_id == S009_Vessel.id', lazy='dynamic')


class S010_Voyage(db.Model):
    __tablename__ = 's010_voyage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    vessel_id = db.Column(db.Integer, db.ForeignKey("s009_vessel.id"))
    rotation_number = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_s010_voyage_vessel_id', 'vessel_id'),
    )

    manifests = db.relationship('S001_Manifest', back_populates='voyage', primaryjoin='S001_Manifest.voyage_id == S010_Voyage.id', lazy='dynamic')
    vessel = db.relationship('S009_Vessel', back_populates='voyages', foreign_keys=[vessel_id])
    legs = db.relationship('S011_Leg', back_populates='voyage', primaryjoin='S011_Leg.voyage_id == S010_Voyage.id', lazy='dynamic')


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
        Index('ix_s011_leg_port_id', 'port_id'),
    )

    voyage = db.relationship('S010_Voyage', back_populates='legs', foreign_keys=[voyage_id])
    port = db.relationship('S012_Port', back_populates='legs', foreign_keys=[port_id])


class S012_Port(db.Model):
    __tablename__ = 's012_port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("s014_country.id"))
    prefix = db.Column(db.String(255))

    __table_args__ = (
        Index('ix_s012_port_country_id', 'country_id'),
    )

    manifest_as_port_of_loadings = db.relationship('S001_Manifest', back_populates='port_of_loading', primaryjoin='S001_Manifest.port_of_loading_id == S012_Port.id', lazy='dynamic')
    manifest_as_port_of_discharges = db.relationship('S001_Manifest', back_populates='port_of_discharge', primaryjoin='S001_Manifest.port_of_discharge_id == S012_Port.id', lazy='dynamic')
    containers = db.relationship('S005_Container', back_populates='port', primaryjoin='S005_Container.port_id == S012_Port.id', lazy='dynamic')
    container_histories = db.relationship('S006_ContainerHistory', back_populates='port', primaryjoin='S006_ContainerHistory.port_id == S012_Port.id', lazy='dynamic')
    legs = db.relationship('S011_Leg', back_populates='port', primaryjoin='S011_Leg.port_id == S012_Port.id', lazy='dynamic')
    country = db.relationship('S014_Country', back_populates='ports', foreign_keys=[country_id])
    port_pair_as_pols = db.relationship('S013_PortPair', back_populates='pol', primaryjoin='S013_PortPair.pol_id == S012_Port.id', lazy='dynamic')
    port_pair_as_pods = db.relationship('S013_PortPair', back_populates='pod', primaryjoin='S013_PortPair.pod_id == S012_Port.id', lazy='dynamic')


class S013_PortPair(db.Model):
    __tablename__ = 's013_portpair'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    pol_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    pod_id = db.Column(db.Integer, db.ForeignKey("s012_port.id"))
    distance = db.Column(db.Integer)
    distance_rate_code = db.Column(db.Integer)

    __table_args__ = (
        Index('ix_s013_portpair_pol_id', 'pol_id'),
        Index('ix_s013_portpair_pod_id', 'pod_id'),
    )

    pol = db.relationship('S012_Port', back_populates='port_pair_as_pols', foreign_keys=[pol_id])
    pod = db.relationship('S012_Port', back_populates='port_pair_as_pods', foreign_keys=[pod_id])


class S014_Country(db.Model):
    __tablename__ = 's014_country'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)

    ports = db.relationship('S012_Port', back_populates='country', primaryjoin='S012_Port.country_id == S014_Country.id', lazy='dynamic')
    clients = db.relationship('S015_Client', back_populates='country', primaryjoin='S015_Client.country_id == S014_Country.id', lazy='dynamic')


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
        Index('ix_s015_client_country_id', 'country_id'),
    )

    manifest_as_shippers = db.relationship('S001_Manifest', back_populates='shipper', primaryjoin='S001_Manifest.shipper_id == S015_Client.id', lazy='dynamic')
    manifest_as_consignees = db.relationship('S001_Manifest', back_populates='consignee', primaryjoin='S001_Manifest.consignee_id == S015_Client.id', lazy='dynamic')
    container_histories = db.relationship('S006_ContainerHistory', back_populates='client', primaryjoin='S006_ContainerHistory.client_id == S015_Client.id', lazy='dynamic')
    country = db.relationship('S014_Country', back_populates='clients', foreign_keys=[country_id])
    rates = db.relationship('S017_Rate', back_populates='client', primaryjoin='S017_Rate.client_id == S015_Client.id', lazy='dynamic')


class S016_User(db.Model):
    __tablename__ = 's016_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))

    manifests = db.relationship('S001_Manifest', back_populates='user', primaryjoin='S001_Manifest.user_id == S016_User.id', lazy='dynamic')
    line_items = db.relationship('S002_LineItem', back_populates='user', primaryjoin='S002_LineItem.user_id == S016_User.id', lazy='dynamic')


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
        Index('ix_s017_rate_client_id', 'client_id'),
    )

    commodity = db.relationship('S003_Commodity', back_populates='rates', foreign_keys=[commodity_id])
    pack_type = db.relationship('S004_PackType', back_populates='rates', foreign_keys=[pack_type_id])
    client = db.relationship('S015_Client', back_populates='rates', foreign_keys=[client_id])


