import unittest
from pathlib import Path
import json
import sys
import tempfile
import os
import shutil
from unittest.mock import patch, mock_open

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from dsl.convert_batch import main

class TestConversionIntegration(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))
        
        # Create all required directories
        self.dsl_dir = Path(self.temp_dir) / 'schemas' / 'test' / 'current'
        self.json_dir = Path(self.temp_dir) / 'output' / 'json'
        self.models_dir = Path(self.temp_dir) / 'output' / 'models'
        self.flask_models_dir = Path(self.temp_dir) / 'app' / 'models'
        
        for dir_path in [self.dsl_dir, self.json_dir, self.models_dir, self.flask_models_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Sample DSL content
        self.sample_dsl = """
    table TestModel {
      id Int [pk, increment]
      name String
      description String
      created_at DateTime
      is_active Boolean
      price Float
      details Text
      parent_id Int [ref: > TestModel.id]
      children TestModel[] [relationship: "one-to-many", back_populates: "parent"]
    }
    """
        
        # Create test DSL file
        self.dsl_file = self.dsl_dir / 'schema.dsl'
        with open(self.dsl_file, 'w') as f:
            f.write(self.sample_dsl)

    def get_mock_config(self, schema_file):
        """Get mock configuration with correct absolute paths"""
        return {
            'paths': {
                'schema_dir': str(schema_file.parent),
                'schema_file': schema_file.name,
                'output_json_dir': str(self.json_dir),
                'output_json_file': 'test.json',
                'output_models_dir': str(self.models_dir),
                'output_models_file': 'test.py',
                'flask_models_dir': str(self.flask_models_dir),
                'flask_models_file': 'test.py'
            },
            'table_naming': {
                'format': 'lower',
                'prefix': '',
                'suffix': ''
            },
            'column_constraints': {
                'primary_key': 'primary_key=True',
                'auto_increment': 'autoincrement=True',
                'nullable': 'nullable=False',
                'unique': 'unique=True'
            }
        }

    def test_end_to_end_conversion(self):
        """Test complete DSL to SQLAlchemy model conversion process"""
        with patch('scripts.convert.get_config') as mock_config:
            mock_config.return_value = self.get_mock_config(self.dsl_file)
            
            # Run conversion
            main()
            
            # Verify output files were created
            self.assertTrue((self.json_dir / 'test.json').exists())
            self.assertTrue((self.models_dir / 'test.py').exists())
            self.assertTrue((self.flask_models_dir / 'test.py').exists())

    def test_missing_schema_file(self):
        """Test handling of missing schema file"""
        non_existent_file = self.dsl_dir / 'non_existent.dsl'
        
        with patch('scripts.convert.get_config') as mock_config:
            mock_config.return_value = self.get_mock_config(non_existent_file)
            
            # Should exit with error
            with self.assertRaises(SystemExit) as cm:
                main()
            
            # Check exit code
            self.assertEqual(cm.exception.code, 1)

    def test_invalid_dsl_content(self):
        """Test handling of invalid DSL content"""
        # Create file with invalid DSL
        invalid_dsl = """
        invalid content
        not a valid DSL file
        """
        invalid_file = self.dsl_dir / 'invalid.dsl'
        with open(invalid_file, 'w') as f:
            f.write(invalid_dsl)
        
        with patch('scripts.convert.get_config') as mock_config:
            mock_config.return_value = self.get_mock_config(invalid_file)
            
            # Should exit with error
            with self.assertRaises(SystemExit) as cm:
                main()
            
            # Check exit code
            self.assertEqual(cm.exception.code, 1)

    def test_all_field_types(self):
        """Test conversion with all supported field types"""
        all_types_dsl = """
    table AllTypes {
      id Int [pk, increment]
      string_field String
      text_field Text
      int_field Int
      float_field Float
      decimal_field Decimal [precision: 10, scale: 2]
      datetime_field DateTime
      date_field Date
      time_field Time
      bool_field Boolean
    }
    """
        
        # Create test file
        all_types_file = self.dsl_dir / 'all_types.dsl'
        with open(all_types_file, 'w') as f:
            f.write(all_types_dsl)
        
        with patch('scripts.convert.get_config') as mock_config:
            mock_config.return_value = self.get_mock_config(all_types_file)
            
            # Run conversion
            main()
            
            # Verify output files were created
            self.assertTrue((self.json_dir / 'test.json').exists())
            self.assertTrue((self.models_dir / 'test.py').exists())
            self.assertTrue((self.flask_models_dir / 'test.py').exists())
            
            # Read generated model file and verify field types
            with open(self.models_dir / 'test.py') as f:
                content = f.read()
                self.assertIn('db.String', content)
                self.assertIn('db.Text', content)
                self.assertIn('db.Integer', content)
                self.assertIn('db.Float', content)
                self.assertIn('db.Decimal', content)
                self.assertIn('db.DateTime', content)
                self.assertIn('db.Date', content)
                self.assertIn('db.Time', content)
                self.assertIn('db.Boolean', content)

if __name__ == '__main__':
    unittest.main()
