from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class S001_Manifest(Base):
    __tablename__ = 's001_manifest'
    id = Column(Integer, primary_key=True, nullable=False)
    bill_of_lading = Column(String, unique=True)
    shipper_id = Column(Integer, ForeignKey('s015_client.id'))
    consignee_id = Column(Integer, ForeignKey('s015_client.id'))
    vessel_id = Column(Integer, ForeignKey('s009_vessel.id'))
    voyage_id = Column(Integer, ForeignKey('s010_voyage.id'))
    port_of_loading_id = Column(Integer, ForeignKey('s012_port.id'))
    port_of_discharge_id = Column(Integer, ForeignKey('s012_port.id'))
    place_of_delivery = Column(String)
    place_of_receipt = Column(String)
    clauses = Column(String)
    date_of_receipt = Column(String)


class S002_LineItem(Base):
    __tablename__ = 's002_lineitem'
    id = Column(Integer, primary_key=True, nullable=False)
    manifest_id = Column(Integer, ForeignKey('s001_manifest.id'))
    description = Column(String)
    quantity = Column(Integer)
    weight = Column(Integer)
    volume = Column(Integer)
    pack_type_id = Column(Integer, ForeignKey('s004_packtype.id'))
    commodity_id = Column(Integer, ForeignKey('s003_commodity.id'))
    container_id = Column(Integer, ForeignKey('s005_container.id'))


class S003_Commodity(Base):
    __tablename__ = 's003_commodity'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    description = Column(String)


class S004_PackType(Base):
    __tablename__ = 's004_packtype'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    description = Column(String)


class S005_Container(Base):
    __tablename__ = 's005_container'
    id = Column(Integer, primary_key=True, nullable=False)
    number = Column(String)
    port_id = Column(Integer, ForeignKey('s012_port.id'))
    updated = Column(String)


class S006_ContainerHistory(Base):
    __tablename__ = 's006_containerhistory'
    id = Column(Integer, primary_key=True, nullable=False)
    container_id = Column(Integer, ForeignKey('s005_container.id'))
    port_id = Column(Integer, ForeignKey('s012_port.id'))
    client_id = Column(Integer, ForeignKey('s015_client.id'))
    container_status_id = Column(Integer, ForeignKey('s007_containerstatus.id'))
    damage = Column(String)
    updated = Column(String)


class S007_ContainerStatus(Base):
    __tablename__ = 's007_containerstatus'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    description = Column(String)


class S008_ShippingCompany(Base):
    __tablename__ = 's008_shippingcompany'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)


class S009_Vessel(Base):
    __tablename__ = 's009_vessel'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    shipping_company_id = Column(Integer, ForeignKey('s008_shippingcompany.id'))


class S010_Voyage(Base):
    __tablename__ = 's010_voyage'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    vessel_id = Column(Integer, ForeignKey('s009_vessel.id'))
    rotation_number = Column(Integer)


class S011_Leg(Base):
    __tablename__ = 's011_leg'
    id = Column(Integer, primary_key=True, nullable=False)
    voyage_id = Column(Integer, ForeignKey('s010_voyage.id'))
    port_id = Column(Integer, ForeignKey('s012_port.id'))
    leg_number = Column(Integer)
    eta = Column(String)
    etd = Column(String)


class S012_Port(Base):
    __tablename__ = 's012_port'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    country_id = Column(Integer, ForeignKey('s014_country.id'))
    prefix = Column(String)


class S013_PortPair(Base):
    __tablename__ = 's013_portpair'
    id = Column(Integer, primary_key=True, nullable=False)
    pol_id = Column(Integer, ForeignKey('s012_port.id'))
    pod_id = Column(Integer, ForeignKey('s012_port.id'))
    distance = Column(Integer)
    distance_rate_code = Column(String)


class S014_Country(Base):
    __tablename__ = 's014_country'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)


class S015_Client(Base):
    __tablename__ = 's015_client'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    address = Column(String)
    town = Column(String)
    country_id = Column(Integer, ForeignKey('s014_country.id'))
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)


class S016_User(Base):
    __tablename__ = 's016_user'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)


class S017_Rate(Base):
    __tablename__ = 's017_rate'
    id = Column(Integer, primary_key=True, nullable=False)
    distance_rate_code = Column(Integer)
    commodity_id = Column(Integer, ForeignKey('s003_commodity.id'))
    pack_type_id = Column(Integer, ForeignKey('s004_packtype.id'))
    client_id = Column(Integer, ForeignKey('s015_client.id'))
    rate = Column(String)
    effective = Column(String)

