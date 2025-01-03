import unittest
from pathlib import Path
import json
import sys
from unittest.mock import patch, mock_open

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from dsl.convert_batch import (
    get_field_type_mapping,
    get_table_name,
    get_constraint_str,
    generate_relationships,
    get_config
)

class TestConversion(unittest.TestCase):
    def setUp(self):
        self.config = get_config()
        self.sample_json = {
            "Models": {
                "S001_Test": {
                    "Fields": {
                        "id": {
                            "type": "Integer",
                            "primary_key": True,
                            "nullable": False,
                            "auto_increment": True
                        },
                        "name": {
                            "type": "String",
                            "max_length": 100
                        },
                        "parent_id": {
                            "type": "Integer",
                            "foreign_key": "s001_test.id",
                            "relationship": {
                                "field_name": "parent",
                                "target_model": "S001_Test",
                                "back_populates": "children"
                            }
                        }
                    },
                    "Relationships": [
                        {
                            "type": "one-to-many",
                            "back_populates": "parent",
                            "target_model": "S001_Test",
                            "field_name": "children"
                        }
                    ]
                }
            }
        }

    def test_field_type_mapping(self):
        """Test field type mapping with various parameters"""
        type_mapping = get_field_type_mapping()
        
        # Test String type with length
        self.assertEqual(type_mapping['String'](100), 'db.String(100)')
        
        # Test Integer type
        self.assertEqual(type_mapping['Integer'](), 'db.Integer')
        
        # Test Decimal type with precision and scale
        self.assertEqual(
            type_mapping['Decimal'](precision=12, scale=3),
            'db.Decimal(precision=12, scale=3)'
        )

    def test_table_name_generation(self):
        """Test table name generation with different configurations"""
        # Test lowercase
        config = {'table_naming': {'format': 'lower', 'prefix': '', 'suffix': ''}}
        self.assertEqual(get_table_name('TestModel', config), 'testmodel')
        
        # Test uppercase
        config = {'table_naming': {'format': 'upper', 'prefix': '', 'suffix': ''}}
        self.assertEqual(get_table_name('TestModel', config), 'TESTMODEL')
        
        # Test with prefix and suffix
        config = {'table_naming': {'format': 'lower', 'prefix': 'pre_', 'suffix': '_sfx'}}
        self.assertEqual(get_table_name('TestModel', config), 'pre_testmodel_sfx')

    def test_constraint_generation(self):
        """Test constraint string generation"""
        # Test primary key constraint
        self.assertEqual(
            get_constraint_str('primary_key', self.config),
            'primary_key=True'
        )
        
        # Test non-existent constraint
        self.assertEqual(
            get_constraint_str('non_existent', self.config),
            ''
        )

    def test_relationship_generation(self):
        """Test relationship generation from JSON data"""
        relationships = generate_relationships(self.sample_json)
        
        # Check if relationships were generated for the test model
        self.assertIn('S001_Test', relationships)
        
        # Check if both relationships are present
        rel_strings = relationships['S001_Test']
        self.assertEqual(len(rel_strings), 2)
        
        # Check parent relationship
        parent_rel = next(r for r in rel_strings if 'parent =' in r)
        self.assertIn('foreign_keys=[parent_id]', parent_rel)
        self.assertIn("backref='s001_test_parent'", parent_rel)
        
        # Check children relationship
        children_rel = next(r for r in rel_strings if 'children =' in r)
        self.assertIn("lazy='dynamic'", children_rel)
        self.assertIn("backref='s001_test_children'", children_rel)

    def test_invalid_field_type(self):
        """Test handling of invalid field type"""
        type_mapping = get_field_type_mapping()
        self.assertNotIn('InvalidType', type_mapping)

    def test_relationship_naming_conflicts(self):
        """Test handling of potential relationship naming conflicts"""
        # Create a model with multiple relationships to the same target
        json_data = {
            "Models": {
                "S001_Test": {
                    "Fields": {
                        "created_by_id": {
                            "type": "Integer",
                            "foreign_key": "s002_user.id",
                            "relationship": {
                                "field_name": "created_by",
                                "target_model": "S002_User",
                                "back_populates": "created_items"
                            }
                        },
                        "updated_by_id": {
                            "type": "Integer",
                            "foreign_key": "s002_user.id",
                            "relationship": {
                                "field_name": "updated_by",
                                "target_model": "S002_User",
                                "back_populates": "updated_items"
                            }
                        }
                    }
                }
            }
        }
        
        relationships = generate_relationships(json_data)
        
        # Check if both relationships were generated with unique names
        rel_strings = relationships['S001_Test']
        self.assertEqual(len(rel_strings), 2)
        
        # Verify unique backref names
        self.assertTrue(any("backref='s001_test_created_by'" in r for r in rel_strings))
        self.assertTrue(any("backref='s001_test_updated_by'" in r for r in rel_strings))

if __name__ == '__main__':
    unittest.main()
