import os
import sys
import random
from datetime import datetime, timedelta
import logging

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from flask import Flask
from app.models.shipping import db
from app.models.shipping import (
    Manifest, LineItem, Commodity, PackType,
    Container, ContainerHistory, ContainerStatus,
    ShippingCompany, Vessel, Voyage, Leg,
    Port, PortPair, Country, Client, User,
    Rate
)

def generate_container_number(owner_code, equipment_type, serial_number):
    """
    Generate an ISO 6346-compliant container number.
    Args:
        owner_code (str): The 4-letter owner code (e.g., MAEU, CSQU).
        equipment_type (str): The 3-character equipment identifier (e.g., 22G, 45R).
        serial_number (int): The 6-digit unique serial number.
    Returns:
        str: A valid container number with a check digit.
    """
    container_base = f"{owner_code}{equipment_type}{serial_number:06d}"
    
    # Calculate the check digit
    char_weights = {str(i): i for i in range(10)}
    char_weights.update({chr(i): i - 55 for i in range(65, 91)})  # A=10, B=11, ..., Z=35
    total = sum(char_weights[char] * (2 ** idx) for idx, char in enumerate(container_base))
    check_digit = total % 11
    check_digit = 0 if check_digit == 10 else check_digit

    return f"{container_base}{check_digit}"

def generate_bill_of_lading(voyage, pol, pod, sequence_counters):
    """
    Generate a bill of lading number in the format: VOYAGE-ROT-POL-POD-SEQ
    """
    # Get voyage abbreviation (first letter of each word, max 4 letters)
    voyage_name = ''.join(word[0].upper() for word in voyage.name.split())[:4]
    
    # Get port codes
    pol_code = pol.prefix[-3:]  # Last 3 chars of port prefix
    pod_code = pod.prefix[-3:]  # Last 3 chars of port prefix
    
    # Create the combination key for sequence tracking
    combo_key = f"{voyage_name}-{voyage.rotation_number:03d}-{pol_code}-{pod_code}"
    
    # Get and increment sequence number
    if combo_key not in sequence_counters:
        sequence_counters[combo_key] = 1
    else:
        sequence_counters[combo_key] += 1
    
    # Format the bill of lading number
    return f"{combo_key}-{sequence_counters[combo_key]:05d}"


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app with minimal configuration
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Debug configuration
logger.debug("Project root: %s", project_root)
logger.debug("SQLAlchemy Database URI: %s", app.config['SQLALCHEMY_DATABASE_URI'])
logger.debug("Debug mode: %s", app.config['DEBUG'])

# Initialize database with app
db.init_app(app)

def verify_table_creation():
    """Verify that all tables were created successfully."""
    try:
        inspector = db.inspect(db.engine)
        expected_tables = {
            'country', 'port', 'client', 'shippingcompany', 'vessel', 'voyage',
            'leg', 'container', 'containerhistory', 'containerstatus', 'manifest',
            'lineitem', 'commodity', 'packtype', 'portpair', 'user', 'rate'
        }
        actual_tables = set(inspector.get_table_names())
        missing_tables = expected_tables - actual_tables
        
        logger.debug("Expected tables: %s", expected_tables)
        logger.debug("Actual tables: %s", actual_tables)
        
        if missing_tables:
            raise Exception(f"Failed to create tables: {', '.join(missing_tables)}")
        
        logger.info("Successfully verified creation of %d tables", len(actual_tables))
        return True
    except Exception as e:
        logger.error("Error during table verification: %s", str(e))
        raise

def populate_data():
    try:
        logger.info("Starting to populate data...")
        
        # Dictionary to track sequence numbers
        sequence_counters = {}

        # Drop all tables and recreate them
        logger.info("Dropping existing tables...")
        # Close any existing connections
        db.session.close()
        db.engine.dispose()
        
        # Get database path and ensure directory exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        
        logger.info("Using database at: %s", db_path)
        logger.info("Database directory: %s", db_dir)
        
        # Debug database configuration
        logger.debug("Database engine: %s", db.engine)
        logger.debug("Database session: %s", db.session)
        
        # Create database directory if it doesn't exist
        if not os.path.exists(db_dir):
            logger.info("Creating database directory: %s", db_dir)
            os.makedirs(db_dir)
            logger.info("Database directory created successfully")
            
        # Delete existing database file
        if os.path.exists(db_path):
            try:
                logger.info("Removing existing database file: %s", db_path)
                os.remove(db_path)
                logger.info("Existing database file removed successfully")
            except PermissionError as e:
                logger.error("Could not delete existing database file: %s", str(e))
                logger.error("Please ensure you have proper permissions")
                raise
        
        logger.info("Creating tables...")
        
        # Debug model metadata
        logger.debug("Model metadata tables: %s", db.Model.metadata.tables.keys())
        
        # Create tables with explicit bind
        db.Model.metadata.create_all(bind=db.engine)
        db.create_all()
        
        # Verify all tables were created
        verify_table_creation()

        # Populate Level 1: Static Context
        # Populate Level 1: Static Context
        print("Populating countries...")
        countries = [
            Country(name=country)
            for country in ["USA", "Netherlands", "China", "India", "Germany", "UK", "Japan", "Australia", "Singapore", "Brazil"]
        ]
        db.session.add_all(countries)
        db.session.commit()

        print("Populating ports...")
        ports = [
            Port(name=name, country_id=random.randint(1, len(countries)), prefix=prefix)
            for i, (name, prefix) in enumerate([
                ("Port of Los Angeles", "USLAX"),
                ("Port of Rotterdam", "NLRTM"),
                ("Shanghai Port", "CNSHA"),
                ("Port of Mumbai", "INBOM"),
                ("Hamburg Port", "DEHAM"),
                ("London Gateway", "GBLGP"),
                ("Yokohama Port", "JPYOK"),
                ("Sydney Harbor", "AUSYD"),
                ("Port of Singapore", "SGSIN"),
                ("Santos Port", "BRSTS")
            ], start=1)
        ]
        db.session.add_all(ports)
        db.session.commit()

        print("Populating shipping companies...")
        companies = [
            ShippingCompany(name=name)
            for name in ["Maersk Line", "CMA CGM", "MSC"]
        ]
        db.session.add_all(companies)
        db.session.commit()

        print("Populating pack types...")
        packtypes = [
            PackType(name=type_name, description=f"{type_name} Description")
            for type_name in ["20ft Container", "40ft Container", "Refrigerated Container", "Flat Rack Container"]
        ]
        db.session.add_all(packtypes)
        db.session.commit()

        print("Populating container statuses...")
        statuses = [
            ContainerStatus(name=status, description=f"Container is {status.lower()}")
            for status in ["In Transit", "At Port", "Loaded", "Damaged"]
        ]
        db.session.add_all(statuses)
        db.session.commit()

        # Company name components for generating realistic business names
        company_prefixes = ["Global", "Inter", "Trans", "Pacific", "Atlantic", "Euro", "Asian", "United", "International", "Premier"]
        company_types = ["Logistics", "Trading", "Imports", "Exports", "Freight", "Supply Chain", "Distribution", "Shipping", "Cargo", "Transport"]
        company_suffixes = ["Corp", "Ltd", "Inc", "Group", "Holdings", "Solutions", "Services", "International", "Enterprises", "Partners"]
        
        # Street names for realistic addresses
        street_types = ["Street", "Avenue", "Boulevard", "Road", "Lane", "Drive", "Way", "Plaza", "Court", "Park"]
        street_names = ["Commerce", "Industry", "Trade", "Harbor", "Port", "Maritime", "Shipping", "Business", "Enterprise", "Corporate"]
        
        # First and last names for contact persons
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Christopher",
                      "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                     "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris"]

        # Cities with their corresponding country IDs
        city_country_mapping = [
            ("Los Angeles", 1), ("San Francisco", 1), ("New York", 1),  # USA
            ("Rotterdam", 2), ("Amsterdam", 2), ("Antwerp", 2),  # Netherlands
            ("Shanghai", 3), ("Shenzhen", 3), ("Guangzhou", 3),  # China
            ("Mumbai", 4), ("Chennai", 4), ("Kolkata", 4),  # India
            ("Hamburg", 5), ("Bremen", 5), ("Düsseldorf", 5),  # Germany
        ]

        clients = []
        for i in range(300):
            # Generate company name with unique identifier
            company_name = f"{random.choice(company_prefixes)} {random.choice(company_types)} {random.choice(company_suffixes)} {i+1:03d}"
            
            # Generate address
            street_number = random.randint(1, 999)
            street = f"{random.choice(street_names)} {random.choice(street_types)}"
            
            # Select city and corresponding country
            city, country_id = random.choice(city_country_mapping)
            
            # Generate contact person
            contact_first = random.choice(first_names)
            contact_last = random.choice(last_names)
            contact_person = f"{contact_first} {contact_last}"
            
            # Generate business email
            email_domain = company_name.lower().split()[0] + ".com"
            email = f"{contact_first.lower()}.{contact_last.lower()}@{email_domain}"
            
            # Generate international phone number based on country
            country_codes = {1: "1", 2: "31", 3: "86", 4: "91", 5: "49"}  # USA, Netherlands, China, India, Germany
            area_code = random.randint(100, 999)
            local_number = random.randint(1000000, 9999999)
            phone = f"+{country_codes[country_id]} {area_code} {local_number}"
            
            client = Client(
                name=company_name,
                address=f"{street_number} {street}",
                town=city,
                country_id=country_id,
                contact_person=contact_person,
                email=email,
                phone=phone
            )
            clients.append(client)
        
        print("Populating clients...")
        db.session.add_all(clients)
        db.session.commit()

        print("Populating commodities...")
        commodities = [
            Commodity(name=name, description=f"Shipments of {name.lower()}")
            for name in ["Electronics", "Machinery", "Textiles", "Furniture", "Automobiles"]
        ]
        db.session.add_all(commodities)
        db.session.commit()

        print("Populating users...")
        users = [
            User(name=role, email=f"{role.lower().replace(' ', '_')}@harbor.com", password_hash="hashed_password")
            for role in ["Operations Manager", "Harbor Master", "Shipping Clerk", "Cargo Inspector", "Logistics Coordinator"]
        ]
        db.session.add_all(users)
        db.session.commit()

        # Populate Level 2
        print("Populating vessels...")
        vessels = [
            Vessel(name=name, shipping_company_id=random.randint(1, len(companies)))
            for name in ["MV Atlantic Star", "SS Oceanic", "HMS Victory", "Evergreen"]
        ]
        db.session.add_all(vessels)
        db.session.commit()

        print("Populating port pairs...")
        port_pairs = [
            PortPair(
                pol_id=random.randint(1, len(ports)), pod_id=random.randint(1, len(ports)),
                distance=random.randint(500, 2000), distance_rate_code=f"RATE_{i:03d}"
            )
            for i in range(50)
        ]
        db.session.add_all(port_pairs)
        db.session.commit()

        # Populate Level 3
        print("Populating voyages...")
        voyages = [
            Voyage(
                name=f"{random.choice([
                    'Asia Express Line',
                    'Trans Pacific Service',
                    'Europe Direct Route',
                    'Mediterranean Link',
                    'Atlantic Connection',
                    'Americas Service',
                    'Far East Loop',
                    'Indian Ocean Circuit',
                    'Global Express',
                    'Pacific Rim Route'
                ])} {i+1:03d}",
                vessel_id=random.randint(1, len(vessels)),
                rotation_number=random.randint(1, 10)
            )
            for i in range(100)
        ]
        db.session.add_all(voyages)
        db.session.commit()  # Commit voyages to get their IDs

        print("Populating voyage legs...")
        legs = []
        for voyage in voyages:
            # Generate 3-7 legs per voyage
            num_legs = random.randint(3, 7)
            # Create a sequence of ports for this voyage
            voyage_ports = random.sample(ports, num_legs + 1)  # +1 because we need arrival and departure ports
            
            for leg_num in range(num_legs):
                # Calculate dates ensuring they progress logically
                base_date = datetime.now() - timedelta(days=random.randint(0, 30))
                arrival_date = base_date + timedelta(days=leg_num * 3)  # 3 days between port calls
                departure_date = arrival_date + timedelta(days=1)  # 1 day at port
                
                legs.append(
                    Leg(
                        voyage_id=voyage.id,
                        leg_number=leg_num + 1,  # Start from 1
                        port_id=voyage_ports[leg_num].id,
                        eta=arrival_date,
                        etd=departure_date
                    )
                )
        db.session.add_all(legs)
        db.session.commit()

        # Populate Level 4
        print("Populating containers...")
        containers = [
            Container(
                number=generate_container_number(
                    owner_code=random.choice(["MAEU", "CMAU", "CSQU"]),
                    equipment_type=random.choice(["22G", "45R", "20T", "40H"]),
                    serial_number=i
                ),
                port_id=random.randint(1, len(ports)),
                updated=datetime.now()
            )
            for i in range(1, 1001)
        ]
        db.session.add_all(containers)
        db.session.commit()

        print("Populating container histories...")
        container_histories = [
            ContainerHistory(
                container_id=container_id,
                port_id=random.randint(1, len(ports)),
                client_id=random.randint(1, len(clients)),
                container_status_id=random.randint(1, len(statuses)),
                damage=random.choice(["None", "Minor", "Major"]),
                updated=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            for container_id in range(1, 1001)
            for _ in range(5)  # 5 history records per container
        ]
        db.session.add_all(container_histories)
        db.session.commit()

        # Populate Manifests
        print("Populating manifests...")
        manifests = []
        for _ in range(200):
            # Get random voyage and its legs
            voyage = db.session.get(Voyage, random.randint(1, len(voyages)))
            voyage_legs = db.session.query(Leg).filter_by(voyage_id=voyage.id).order_by(Leg.leg_number).all()
            
            # Select a random leg pair for loading and discharge
            leg_idx = random.randint(0, len(voyage_legs) - 2)  # Ensure we have a next leg for discharge
            loading_leg = voyage_legs[leg_idx]
            discharge_leg = voyage_legs[leg_idx + 1]
            
            # Use the leg's ports for POL and POD
            pol = db.session.get(Port, loading_leg.port_id)
            pod = db.session.get(Port, discharge_leg.port_id)
            
            # Generate unique bill of lading
            bl_number = generate_bill_of_lading(voyage, pol, pod, sequence_counters)
            
            manifest = Manifest(
                bill_of_lading=bl_number,
                shipper_id=random.randint(1, len(clients)),
                consignee_id=random.randint(1, len(clients)),
                vessel_id=random.randint(1, len(vessels)),
                voyage_id=voyage.id,
                port_of_loading_id=pol.id,
                port_of_discharge_id=pod.id,
                place_of_delivery=random.choice(["Warehouse A", "Terminal B", "Distribution Center C"]),
                place_of_receipt=random.choice(["Factory X", "Supplier Y", "Warehouse Z"]),
                clauses="Standard shipping terms apply",
                date_of_receipt=datetime.now(),
                user_id=random.randint(1, len(users))
            )
            manifests.append(manifest)
        db.session.add_all(manifests)
        db.session.commit()  # Commit to get manifest IDs

        print("Populating line items...")
        line_items = []
        for manifest in manifests:
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                line_items.append(
                    LineItem(
                        manifest_id=manifest.id,
                        description=f"Cargo item for {manifest.bill_of_lading}",
                        quantity=random.randint(1, 100),
                        weight=random.randint(100, 5000),
                        volume=random.randint(1, 100),
                        pack_type_id=random.randint(1, len(packtypes)),
                        commodity_id=random.randint(1, len(commodities)),
                        container_id=random.randint(1, len(containers))
                    )
                )
        db.session.add_all(line_items)
        db.session.commit()

        print("Populating rates...")
        rates = [
            Rate(
                distance_rate_code=random.randint(100, 999),
                commodity_id=random.randint(1, len(commodities)),
                pack_type_id=random.randint(1, len(packtypes)),
                client_id=random.randint(1, len(clients)),
                rate=str(random.randint(15, 200)),
                effective=datetime.now()
            )
            for _ in range(300)
        ]
        db.session.add_all(rates)
        db.session.commit()

        print("All data populated successfully.")
    except Exception as e:
        print(f"Error during data population: {str(e)}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    with app.app_context():
        populate_data()
