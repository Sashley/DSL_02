# DSL Tools for Shipping Domain

This directory contains the Domain Specific Language (DSL) tools for defining and managing shipping domain models.

## Directory Structure

```
dsl/
├── schemas/                   # DSL definition files
│   ├── shipping/             # Shipping domain schemas
│   │   ├── current/          # Current version of schemas
│   │   └── archive/          # Historical versions
│   └── validation/           # Schema validation rules
│
├── converter/                # Conversion tools
│   ├── dsl.py               # DSL parsing
│   ├── json.py              # JSON conversion
│   └── validation.py        # Validation logic
│
├── tests/                   # Test suite
│   ├── test_dsl.py         # DSL conversion tests
│   ├── test_json.py        # JSON conversion tests
│   └── fixtures/           # Test data
│
├── output/                  # Generated files
│   ├── json/               # Intermediate JSON
│   └── models/             # Generated SQLAlchemy models
│
└── scripts/                # Utility scripts
    ├── convert.py         # Main conversion script
    ├── validate.py        # Schema validation script
    ├── populate_db.py     # Database population script
    └── check_db.py        # Database verification script
```

## Installation

First, install the package in development mode:

```bash
# From the directory containing the dsl package:
pip install -e dsl

# Or with absolute path:
pip install -e /path/to/dsl

# On Windows:
pip install -e C:\path\to\dsl
```

## Usage

1. Place your DSL schema in `dsl/schemas/shipping/current/schema.dsl`
2. Run validation:
   ```bash
   python -m dsl.scripts.validate
   ```
3. Convert to SQLAlchemy models:
   ```bash
   python -m dsl.scripts.convert
   ```

Generated files will be placed in:

- JSON schema: `dsl/output/json/shipping.json`
- SQLAlchemy models: `dsl/output/models/shipping.py`
- Flask-SQLAlchemy models: `app/models/shipping.py`

4. (Optional) Populate database with test data:

   ```bash
   python -m dsl.scripts.populate_db
   ```

   This will create a SQLite database (`db/shipping.db`) with comprehensive test data:

   - Base data (countries, ports, companies, etc.)
   - Core shipping data (vessels, voyages, legs, containers)
   - Business data (manifests, line items, rates)

   You can verify the populated data using:

   ```bash
   python -m dsl.scripts.check_db
   ```

   The populate script generates:

   - 200 manifests with unique bill of lading numbers
   - ~1200 line items
   - 1000 containers with 5000 history records
   - 100 voyages with ~500 legs
   - 300 clients with realistic company names and contact details
   - And more supporting reference data

   All data is generated with proper relationships and realistic values, making it suitable for:

   - Development testing
   - UI prototyping
   - Performance testing
   - Demonstration purposes

## Relationship Handling

The DSL tools now provide comprehensive relationship handling with the following features:

### One-to-Many Relationships

Define one-to-many relationships using array notation and relationship attributes:

```
table Parent {
    id Int [pk, increment]
    children Child[] [relationship: "one-to-many", back_populates: "parent"]
}

table Child {
    id Int [pk, increment]
    parent_id Int [ref: > Parent.id]
}
```

The converter will automatically:

- Set up bi-directional relationships
- Configure lazy loading for collections
- Add proper foreign key constraints

### Special Relationships

The tools handle several special relationship types:

1. **Self-referential relationships** (e.g., hierarchical data):

```
table Category {
    id Int [pk, increment]
    parent_id Int [ref: > Category.id]
}
```

2. **Multiple relationships to same model** (e.g., shipping/receiving ports):

```
table PortPair {
    id Int [pk, increment]
    pol_id Int [ref: > Port.id]  # Port of Loading
    pod_id Int [ref: > Port.id]  # Port of Discharge
}
```

3. **Bidirectional relationships with custom names**:

```
table Client {
    id Int [pk, increment]
    manifests Manifest[] [relationship: "one-to-many", back_populates: "shipper"]
    consigned_manifests Manifest[] [relationship: "one-to-many", back_populates: "consignee"]
}
```

### Relationship Features

The converter automatically handles:

1. **Lazy Loading**: Collections are configured with `lazy='dynamic'` for efficient querying
2. **Back References**: All relationships are bi-directional with proper `back_populates`
3. **Foreign Keys**: Proper foreign key constraints are added automatically
4. **Relationship Naming**: Custom relationship names are preserved
5. **Collection Types**: One-to-many relationships use dynamic loading by default

### Best Practices

1. **Always specify back_populates**:

```
# Good
children Child[] [relationship: "one-to-many", back_populates: "parent"]

# Not recommended
children Child[]  # Missing relationship metadata
```

2. **Use meaningful relationship names**:

```
# Good
consigned_manifests Manifest[] [relationship: "one-to-many", back_populates: "consignee"]

# Not recommended
manifests2 Manifest[] [relationship: "one-to-many", back_populates: "client2"]
```

3. **Document complex relationships** with comments:

```
# Port pairs track loading and discharge ports for routes
table PortPair {
    id Int [pk, increment]
    pol_id Int [ref: > Port.id]  # Port of Loading
    pod_id Int [ref: > Port.id]  # Port of Discharge
}
```

## Development

- All conversion logic is in the `converter` package
- Add tests in the `tests` directory
- Generated files go to `output` directory
- Use `archive` directory for version history

## Generated Models

The generated SQLAlchemy models are ready to use out of the box with:

1. All relationships properly configured
2. Bi-directional navigation between related models
3. Efficient lazy loading for collections
4. Proper foreign key constraints
5. Custom relationship names preserved

No manual adjustments to the generated models should be necessary.
