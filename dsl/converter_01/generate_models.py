import json
from typing import Dict

# Template for the SQLAlchemy models file
MODEL_TEMPLATE = """from app import db
from datetime import datetime
from sqlalchemy import Index

# Auto-generated SQLAlchemy models

{models}
"""

CLASS_TEMPLATE = """class {class_name}(db.Model):
    __tablename__ = '{table_name}'
{relationships}
{fields}
"""

FIELD_TEMPLATE = "    {field_name} = db.Column(db.{type}{constraints})"
RELATIONSHIP_TEMPLATE = "    {field_name} = db.relationship('{target_model}', {relationship_args})"

def find_matching_relationship(model_name: str, field_name: str, all_models_data: Dict) -> tuple:
    """Find matching relationship in target model."""
    for target_name, target_data in all_models_data["Models"].items():
        for rel in target_data.get("Relationships", []):
            if rel["target_model"] == model_name and rel["field_name"] == field_name:
                return target_name, rel
    return None, None

def find_relationship_back_populates(model_name: str, field_name: str, target_model: str, all_models_data: Dict) -> str:
    """Find the correct back_populates value for a relationship."""
    # Special cases for Client's manifests
    if model_name == "S015_Client":
        if field_name == "manifests":
            return "shipper"
        elif field_name == "consigned_manifests":
            return "consignee"
        elif field_name == "country":
            return "clients"
    elif model_name == "S001_Manifest":
        if field_name == "shipper":
            return "manifests"
        elif field_name == "consignee":
            return "consigned_manifests"
    elif model_name == "S013_PortPair":
        if field_name == "port_of_loading":
            return "port_pairs_as_loading"
        elif field_name == "port_of_discharge":
            return "port_pairs_as_discharge"
    elif model_name == "S012_Port":
        if field_name == "port_pairs_as_loading":
            return "port_of_loading"
        elif field_name == "port_pairs_as_discharge":
            return "port_of_discharge"
    elif model_name == "S010_Voyage":
        if field_name == "vessel":
            return "voyages"
    elif model_name == "S011_Leg":
        if field_name == "port":
            return "legs"
    elif model_name == "S017_Rate":
        if field_name in ["commodity", "pack_type", "client"]:
            return "rates"
    elif model_name == "S014_Country":
        if field_name == "clients":
            return "country"
    
    # Look for matching relationship in target model
    target_data = all_models_data["Models"].get(target_model, {})
    for rel in target_data.get("Relationships", []):
        if rel["target_model"] == model_name:
            return rel["field_name"]
    
    # Look for relationship in current model
    current_data = all_models_data["Models"].get(model_name, {})
    for rel in current_data.get("Relationships", []):
        if rel["target_model"] == target_model and rel["field_name"] == field_name:
            return rel["back_populates"]
    
    # Default to field name
    return field_name

def generate_relationship_args(rel_data: Dict, model_name: str, all_models_data: Dict) -> str:
    """Generate relationship arguments string."""
    args = []
    
    # Handle relationship type
    if rel_data.get("type") == "one-to-many":
        args.append("lazy='dynamic'")
    
    # Handle back_populates
    if "target_model" in rel_data:
        back_populates = find_relationship_back_populates(
            model_name,
            rel_data["field_name"],
            rel_data["target_model"],
            all_models_data
        )
        args.append(f"back_populates='{back_populates}'")
    
    # Handle special relationships
    if model_name == "S012_Port":
        if rel_data["field_name"] == "port_pairs_as_loading":
            args.append("primaryjoin='S012_Port.id==S013_PortPair.pol_id'")
            args.append("foreign_keys='[S013_PortPair.pol_id]'")
            args.append("viewonly=True")
        elif rel_data["field_name"] == "port_pairs_as_discharge":
            args.append("primaryjoin='S012_Port.id==S013_PortPair.pod_id'")
            args.append("foreign_keys='[S013_PortPair.pod_id]'")
            args.append("viewonly=True")
    elif model_name == "S013_PortPair":
        if rel_data["field_name"] == "port_of_loading":
            args.append("primaryjoin='S013_PortPair.pol_id==S012_Port.id'")
            args.append("foreign_keys='[S013_PortPair.pol_id]'")
        elif rel_data["field_name"] == "port_of_discharge":
            args.append("primaryjoin='S013_PortPair.pod_id==S012_Port.id'")
            args.append("foreign_keys='[S013_PortPair.pod_id]'")
    # Handle other relationships
    elif "foreign_keys" in rel_data:
        model_prefix = model_name.lower()
        args.append(f"foreign_keys='[{model_name}.{rel_data['foreign_keys'][0]}]'")
        # Add overlaps parameter for relationships that share foreign keys
        if model_name == "S001_Manifest":
            if rel_data["field_name"] == "line_items":
                args.append("overlaps='s002_lineitem_manifest'")
        elif model_name == "S002_LineItem":
            if rel_data["field_name"] == "manifest":
                args.append("overlaps='s001_manifest_line_items'")
    
    return ", ".join(args)

def find_reverse_relationship(model_name: str, field_name: str, all_models_data: Dict) -> dict:
    """Find the reverse relationship definition."""
    for target_name, target_data in all_models_data["Models"].items():
        for rel in target_data.get("Relationships", []):
            if rel["target_model"] == model_name and rel["back_populates"] == field_name:
                return {
                    "field_name": field_name,
                    "target_model": target_name,
                    "back_populates": rel["field_name"],
                    "type": "many-to-one"
                }
    return None

def generate_reverse_relationships(model_name: str, fields: Dict, all_models_data: Dict) -> list:
    """Generate reverse side of relationships based on foreign keys."""
    reverse_rels = []
    
    for field_name, field_props in fields.items():
        if "foreign_key" in field_props:
            target_table, target_field = field_props["foreign_key"].split(".")
            rel_name = field_name.replace("_id", "")
            
            # Find matching relationship in target model
            target_model_name = None
            for name in all_models_data["Models"].keys():
                if name.lower() == target_table.lower():
                    target_model_name = name
                    break
            
            if target_model_name:
                # Find matching forward relationship
                reverse_rel = find_reverse_relationship(model_name, rel_name, all_models_data)
                if reverse_rel:
                    reverse_rel["foreign_keys"] = [field_name]
                    reverse_rels.append(reverse_rel)
                else:
                    # Find relationship in target model's relationships
                    target_rel = None
                    target_data = all_models_data["Models"][target_model_name]
                    for rel in target_data.get("Relationships", []):
                        if rel["target_model"] == model_name:
                            target_rel = rel
                            break
                    
                    back_populates = target_rel["field_name"] if target_rel else rel_name
                    
                    # Special handling for relationships
                    if model_name == "S013_PortPair":
                        if field_name == "pol_id":
                            field_def = {
                                "field_name": "port_of_loading",
                                "target_model": target_model_name,
                                "back_populates": "port_pairs_as_loading",
                                "relationship_name": "port_of_loading",
                                "foreign_keys": ["pol_id"]
                            }
                        elif field_name == "pod_id":
                            field_def = {
                                "field_name": "port_of_discharge",
                                "target_model": target_model_name,
                                "back_populates": "port_pairs_as_discharge",
                                "relationship_name": "port_of_discharge",
                                "foreign_keys": ["pod_id"]
                            }
                    elif model_name == "S012_Port":
                        if field_name == "pol_id":
                            field_def = {
                                "field_name": "port_pairs_as_loading",
                                "target_model": "S013_PortPair",
                                "back_populates": "port_of_loading",
                                "relationship_name": "port_pairs_as_loading"
                            }
                        elif field_name == "pod_id":
                            field_def = {
                                "field_name": "port_pairs_as_discharge",
                                "target_model": "S013_PortPair",
                                "back_populates": "port_of_discharge",
                                "relationship_name": "port_pairs_as_discharge"
                            }
                    else:
                        field_def = {
                            "field_name": rel_name,
                            "target_model": target_model_name,
                            "back_populates": back_populates or rel_name,
                            "relationship_name": rel_name,
                            "foreign_keys": [field_name]
                        }
                    field_def["type"] = "many-to-one"
                    reverse_rels.append(field_def)
    
    return reverse_rels

def generate_index_definitions(model_name: str, indices: Dict) -> str:
    """Generate index definitions for a model."""
    if not indices:
        return ""
        
    index_defs = []
    for index_name, index_columns in indices.items():
        columns_str = ", ".join([f"{model_name}.{col}" for col in index_columns])
        index_defs.append(f"Index('{index_name}', {columns_str})")
    
    if index_defs:
        return f"    __table_args__ = ({', '.join(index_defs)},)"
    return ""

def generate_field_definitions(fields: Dict) -> str:
    """Generate field definitions for a model."""
    field_lines = []
    for field_name, field_props in fields.items():
        constraints = []

        if field_props.get("primary_key", False):
            constraints.append("primary_key=True")
        if field_props.get("auto_increment", False):
            constraints.append("autoincrement=True")
        if not field_props.get("nullable", True):
            constraints.append("nullable=False")
        if field_props.get("unique", False):
            constraints.append("unique=True")
        if field_props.get("foreign_key"):
            constraints.append(f"db.ForeignKey('{field_props['foreign_key']}')")

        constraints_str = f", {', '.join(constraints)}" if constraints else ""
        field_lines.append(FIELD_TEMPLATE.format(
            field_name=field_name,
            type=field_props["type"],
            constraints=constraints_str
        ))

    return "\n".join(field_lines)

def generate_models(json_file: str, output_file: str):
    """Generate SQLAlchemy models from a JSON file."""
    with open(json_file, "r") as f:
        data = json.load(f)

    models = []
    for model_name, model_data in data["Models"].items():
        # Get all relationships including reverse ones from foreign keys
        relationships = model_data.get("Relationships", [])
        reverse_rels = generate_reverse_relationships(model_name, model_data["Fields"], data)
        
        # Remove duplicate relationships
        seen_rels = set()
        unique_rels = []
        for rel in relationships + reverse_rels:
            rel_key = (rel["field_name"], rel["target_model"], rel.get("back_populates"))
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                unique_rels.append(rel)

        # Generate relationships with proper foreign key handling
        relationships_str = ""
        for rel in unique_rels:
            rel_args = generate_relationship_args(rel, model_name, data)
            relationships_str += RELATIONSHIP_TEMPLATE.format(
                field_name=rel["field_name"],
                target_model=rel["target_model"],  # Already includes prefix
                relationship_args=rel_args
            ) + "\n"
        
        # Generate fields and indices
        fields = generate_field_definitions(model_data["Fields"])
        indices = generate_index_definitions(model_name, model_data.get("Indices", {}))
        
        # Combine into class
        model_class = CLASS_TEMPLATE.format(
            class_name=model_name,
            table_name=model_name.lower(),
            relationships=relationships_str,
            fields=f"{fields}\n{indices}" if indices else fields
        )
        models.append(model_class)

    # Generate complete file
    full_code = MODEL_TEMPLATE.format(models="\n\n".join(models))

    with open(output_file, "w") as f:
        f.write(full_code)

    print(f"Models written to {output_file}")

if __name__ == "__main__":
    # Example usage
    generate_models("shipping_converted.json", "models.py")
