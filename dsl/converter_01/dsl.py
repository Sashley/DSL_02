import json
import re
from collections import defaultdict

DEFAULT_PARAMS = {
    "nullable": True,
    "default": None,
}

def parse_type(field_type):
    """Parse and map field types."""
    # Extract any parameters from the type
    params = {}
    if '[' in field_type:
        base_type = field_type.split('[')[0]
        param_str = field_type[field_type.index('[')+1:field_type.rindex(']')]
        if param_str:
            for param in param_str.split(','):
                if ':' in param:
                    key, value = param.split(':')
                    params[key.strip()] = value.strip()
    else:
        base_type = field_type

    type_mapping = {
        "Int": "Integer",
        "String": "String",
        "Text": "Text",
        "DateTime": "DateTime",
        "Date": "Date",
        "Time": "Time",
        "Float": "Float",
        "Decimal": "Decimal",
        "Boolean": "Boolean"
    }
    
    mapped_type = type_mapping.get(base_type, "String")
    
    # Add any parameters to the type info
    if params:
        if mapped_type == "Decimal":
            return {
                "type": mapped_type,
                "precision": int(params.get("precision", "10")),
                "scale": int(params.get("scale", "2"))
            }
        elif mapped_type == "String":
            return {
                "type": mapped_type,
                "max_length": int(params.get("length", "40"))
            }
    
    return {"type": mapped_type}

def parse_foreign_key(ref_part, model_map):
    """Parse foreign key references."""
    match = re.search(r'ref: > (\w+)\.(\w+)', ref_part)
    if match:
        target_model, target_field = match.groups()
        return model_map.get(target_model, target_model), target_field
    return None, None

def parse_relationship(field_type, attrs, field_name, model_map):
    """Parse relationship definitions."""
    rel_match = re.search(r'relationship: "([^"]+)"', attrs)
    back_pop_match = re.search(r'back_populates: "([^"]+)"', attrs)
    
    if rel_match and back_pop_match:
        target_model = field_type.replace("[]", "")
        prefixed_target = model_map.get(target_model, target_model)
        return {
            "type": rel_match.group(1),
            "back_populates": back_pop_match.group(1),
            "target_model": prefixed_target,
            "field_name": field_name,
            "relationship_name": back_pop_match.group(1)
        }
    return None

def first_pass_create_model_map(file_path):
    """First pass: Create a mapping of table names to prefixed names."""
    model_map = {}
    model_counter = 1
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("table"):
                table_name = line.split()[1]
                model_map[table_name] = f"S{model_counter:03}_{table_name}"
                model_counter += 1
    return model_map

def second_pass_generate_models(file_path, model_map):
    """Second pass: Process fields, relationships, and indices."""
    result = {
        "version": "1.0",
        "Models": {},
        "Menus": {"Main": [], "Context": {}, "Statistics": {}}
    }
    current_model = None
    current_model_name = None

    # First create all models with empty relationships
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("table"):
                table_name = line.split()[1]
                prefixed_name = model_map[table_name]
                result["Models"][prefixed_name] = {
                    "Fields": {},
                    "Relationships": [],
                    "Indices": {},
                    "Menus": {"Context": [], "Statistics": []}
                }
                result["Menus"]["Main"].append({"table": table_name, "route": f"/view/{table_name}"})

    # First collect all relationships to help with back references
    relationships = defaultdict(list)
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("table"):
                current_model_name = line.split()[1]
            elif "relationship:" in line and "back_populates:" in line:
                rel_info = parse_relationship(
                    line.split()[1],  # field_type
                    line.split(maxsplit=2)[2],  # attrs
                    line.split()[0],  # field_name
                    model_map
                )
                if rel_info:
                    relationships[current_model_name].append(rel_info)

    # Now process everything with relationship context
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("table"):
                # Start of a new table
                table_name = line.split()[1]
                current_model_name = table_name
                prefixed_name = model_map[table_name]
                current_model = result["Models"][prefixed_name]

            elif current_model:
                parts = line.split(maxsplit=2)
                if len(parts) < 2:
                    continue

                field_name, field_type = parts[0], parts[1]
                attrs = parts[2] if len(parts) > 2 else ""

                # Handle relationships (type ending with [])
                if "[]" in field_type:
                    rel_info = parse_relationship(field_type, attrs, field_name, model_map)
                    if rel_info:
                        current_model["Relationships"].append(rel_info)
                        # Add context menu entry
                        current_model["Menus"]["Context"].append({
                            "drill_down": rel_info["target_model"],
                            "route": f"/view/{rel_info['target_model']}?filter={field_name}"
                        })
                    continue

                # Process regular fields
                base_type = field_type.split("[")[0]  # Remove array notation if present
                type_info = parse_type(field_type)
                field_def = type_info if isinstance(type_info, dict) else {"type": type_info}

                # Handle field attributes
                if attrs:
                    if "[pk" in attrs:
                        field_def["primary_key"] = True
                        field_def["nullable"] = False
                    if "increment" in attrs:
                        field_def["auto_increment"] = True
                    if "unique" in attrs:
                        field_def["unique"] = True
                    if "default: `now()`" in attrs:
                        field_def["default"] = "now()"
                    target_model, target_field = parse_foreign_key(attrs, model_map)
                    if target_model and target_field:
                        field_def["foreign_key"] = f"{target_model}.{target_field}".lower()
                        field_def["nullable"] = True
                        
                        # Find matching relationship for back_populates
                        rel_name = field_name.replace("_id", "")
                        back_populates = None
                        
                        # Look for matching relationship in target model
                        for rel in relationships.get(target_model, []):
                            # Check if this relationship targets our current model
                            if rel["target_model"] == model_map.get(current_model_name):
                                back_populates = rel["back_populates"]
                                break
                        
                        # Special handling for PortPair relationships
                        if current_model_name == "PortPair":
                            if field_name == "pol_id":
                                field_def["relationship"] = {
                                    "field_name": "port_of_loading",
                                    "target_model": target_model,
                                    "back_populates": "port_pairs_as_loading",
                                    "foreign_keys": [field_name]
                                }
                            elif field_name == "pod_id":
                                field_def["relationship"] = {
                                    "field_name": "port_of_discharge",
                                    "target_model": target_model,
                                    "back_populates": "port_pairs_as_discharge",
                                    "foreign_keys": [field_name]
                                }
                        else:
                            # Find the matching relationship in the target model
                            target_rel = None
                            for rel in relationships.get(target_model, []):
                                if rel["target_model"] == model_map.get(current_model_name):
                                    target_rel = rel
                                    break
                            
                            # Use the relationship_name from the target model's relationship
                            field_def["relationship"] = {
                                "field_name": rel_name,
                                "target_model": target_model,
                                "back_populates": target_rel["relationship_name"] if target_rel else rel_name,
                                "foreign_keys": [field_name]
                            }

                        # Context menu link for related table
                        current_model["Menus"]["Context"].append({
                            "related_table": target_model,
                            "route": f"/view/{target_model}?filter={field_name}"
                        })

                # Add default parameters for non-primary, non-foreign fields
                if "primary_key" not in field_def and "foreign_key" not in field_def:
                    # Only apply DEFAULT_PARAMS if no default was already set
                    if "default" not in field_def:
                        field_def.update(DEFAULT_PARAMS)
                
                current_model["Fields"][field_name] = field_def

    # Add indices for foreign keys
    for model, data in result["Models"].items():
        for field, details in data["Fields"].items():
            if "foreign_key" in details:
                data["Indices"][f"idx_{field}"] = [field]

    return result

def convert_dsl_to_json(input_file, output_file):
    """Convert DSL file to JSON format."""
    model_map = first_pass_create_model_map(input_file)
    dsl_json = second_pass_generate_models(input_file, model_map)

    # Write to output JSON
    with open(output_file, "w") as f:
        json.dump(dsl_json, f, indent=4)
    
    return dsl_json
