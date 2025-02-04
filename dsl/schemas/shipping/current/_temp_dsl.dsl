table Manifest {
  id Int [pk, increment]
  bill_of_lading String [unique]
  shipper_id Int [ref: > Client.id]
  consignee_id Int [ref: > Client.id]
  vessel_id Int [ref: > Vessel.id]
  voyage_id Int [ref: > Voyage.id]
  port_of_loading_id Int [ref: > Port.id]
  port_of_discharge_id Int [ref: > Port.id]
  place_of_delivery String
  place_of_receipt String
  clauses String
  date_of_receipt DateTime [default: `now()`]
  user_id Int [ref: > User.id]
}

table LineItem {
  id Int [pk, increment]
  manifest_id Int [ref: > Manifest.id]
  description String
  quantity Int
  weight Int
  volume Int
  pack_type_id Int [ref: > PackType.id]
  commodity_id Int [ref: > Commodity.id]
  container_id Int [ref: > Container.id]
  user_id Int [ref: > User.id]
}

table Commodity {
  id Int [pk, increment]
  name String [unique]
  description String
}

table PackType {
  id Int [pk, increment]
  name String [unique]
  description String
}

table Container {
  id Int [pk, increment]
  number String [unique]
  port_id Int [ref: > Port.id]
  updated DateTime [default: `now()`]
}

table ContainerHistory {
  id Int [pk, increment]
  container_id Int [ref: > Container.id]
  port_id Int [ref: > Port.id]
  client_id Int [ref: > Client.id]
  container_status_id Int [ref: > ContainerStatus.id]
  damage String
  updated DateTime [default: `now()`]
}

table ContainerStatus {
  id Int [pk, increment]
  name String []
  description String
}

table ShippingCompany {
  id Int [pk, increment]
  name String [unique]
}

table Vessel {
  id Int [pk, increment]
  name String []
  shipping_company_id Int [ref: > ShippingCompany.id]
}

table Voyage {
  id Int [pk, increment]
  name String [unique]
  vessel_id Int [ref: > Vessel.id]
  rotation_number Int
}

table Leg {
  id Int [pk, increment]
  voyage_id Int [ref: > Voyage.id]
  port_id Int [ref: > Port.id]
  leg_number Int
  eta DateTime [default: `now()`]
  etd DateTime [default: `now()`]
}

table Port {
  id Int [pk, increment]
  name String [unique]
  country_id Int [ref: > Country.id]
  prefix String
}

table PortPair {
  id Int [pk, increment]
  pol_id Int [ref: > Port.id]
  pod_id Int [ref: > Port.id]
  distance Int
  distance_rate_code Int
}

table Country {
  id Int [pk, increment]
  name String [unique]
}

table Client {
  id Int [pk, increment]
  name String [unique]
  address String
  town String
  country_id Int [ref: > Country.id]
  contact_person String
  email String
  phone String
}

table User {
  id Int [pk, increment]
  name String [unique]
  email String
  password_hash String
}

table Rate {
  id Int [pk, increment]
  distance_rate_code Int 
  commodity_id Int [ref: > Commodity.id]
  pack_type_id Int [ref: > PackType.id]
  client_id Int [ref: > Client.id]
  rate Float
  effective DateTime [default: `now()`]
}
