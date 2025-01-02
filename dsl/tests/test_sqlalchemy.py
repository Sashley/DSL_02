import unittest
import os
from sqlalchemy.orm import declarative_base, clear_mappers
from sqlalchemy import MetaData
from json_to_sqlalchemy import load_json_to_models

class TestJSONToSQLAlchemy(unittest.TestCase):
    def setUp(self):
        """
        Set up the DSL JSON for testing and clear existing metadata.
        """
        clear_mappers()  # Reset SQLAlchemy mappers
        self.Base = declarative_base(metadata=MetaData())  # Create a new Base with fresh MetaData
        # Use path relative to the test file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.dsl_json = os.path.join(current_dir, "shipping_converted.json")
        self.models = load_json_to_models(self.dsl_json, self.Base)

    def test_model_creation(self):
        """
        Test that models are dynamically created and have correct attributes.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        # Check attributes
        columns = {c.name for c in manifest.__table__.columns}
        expected_columns = {"id", "bill_of_lading", "shipper_id", "consignee_id"}
        self.assertTrue(expected_columns.issubset(columns), "Expected columns not found in S001_Manifest.")

    def test_foreign_keys(self):
        """
        Test that foreign keys are correctly applied.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        # Validate foreign keys
        foreign_keys = {fk.target_fullname for fk in manifest.__table__.foreign_keys}
        expected_foreign_keys = {"s015_client.id", "s015_client.id"}
        self.assertTrue(expected_foreign_keys.issubset(foreign_keys), "Foreign keys not correctly set.")

    def test_primary_keys(self):
        """
        Test that primary keys are correctly assigned.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        # Check primary key constraints
        primary_keys = {pk.name for pk in manifest.__table__.primary_key}
        self.assertTrue(primary_keys, f"Table 'S001_Manifest' has no primary key.")
        self.assertIn("id", primary_keys, "Primary key 'id' is missing in S001_Manifest.")

    def test_nullable_fields(self):
        """
        Test that nullable fields are correctly set.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        nullable_columns = {col.name for col in manifest.__table__.columns if col.nullable}
        expected_nullable = {"bill_of_lading", "shipper_id", "consignee_id"}
        self.assertTrue(expected_nullable.issubset(nullable_columns), "Nullable fields are not correctly set.")


    def test_unique_constraints(self):
        """
        Test that unique constraints are correctly applied.
        """
        # Adjust based on actual fields marked as unique
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        unique_columns = {col.name for col in manifest.__table__.columns if col.unique}
        expected_unique = {"bill_of_lading"}  # Replace with the actual unique fields
        self.assertTrue(expected_unique.issubset(unique_columns), "Unique constraints are not correctly set.")


    def test_relationship_mapping(self):
        """
        Test that relationships are correctly mapped.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        # Check for relationship properties
        relationship_names = {rel.key for rel in manifest.__mapper__.relationships}
        expected_relationships = {"shipper_id_rel", "consignee_id_rel"}  # Adjust based on your foreign key mappings
        self.assertTrue(expected_relationships.issubset(relationship_names), "Relationships are not correctly set.")

        def test_auto_increment_fields(self):
            """
            Test that auto-increment fields are correctly set.
            """
            manifest = self.models.get("S001_Manifest")
            self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

            auto_increment_columns = {
                col.name for col in manifest.__table__.columns if col.autoincrement
            }
            expected_auto_increment = {"id"}
            self.assertTrue(expected_auto_increment.issubset(auto_increment_columns), "Auto-increment fields are not correctly set.")

    def test_missing_or_extra_fields(self):
        """
        Test that all fields in the JSON are present in the generated model.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        model_columns = {col.name for col in manifest.__table__.columns}
        expected_columns = {
            "id", "bill_of_lading", "shipper_id", "consignee_id",
            "vessel_id", "voyage_id", "port_of_loading_id", "port_of_discharge_id",
            "place_of_delivery", "place_of_receipt", "clauses", "date_of_receipt"
        }
        self.assertEqual(model_columns, expected_columns, "Mismatch between JSON fields and model columns.")


    def test_indexes(self):
        """
        Test that indexes are correctly created.
        """
        manifest = self.models.get("S001_Manifest")
        self.assertIsNotNone(manifest, "Model S001_Manifest was not created.")

        indexes = {idx.name for idx in manifest.__table__.indexes}
        expected_indexes = {
            "idx_shipper_id", "idx_consignee_id", "idx_vessel_id", 
            "idx_voyage_id", "idx_port_of_loading_id", "idx_port_of_discharge_id"
        }
        self.assertTrue(expected_indexes.issubset(indexes), "Indexes are not correctly set.")
    
 
if __name__ == "__main__":
    unittest.main()
