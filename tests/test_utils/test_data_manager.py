import pytest
import json
import yaml
from pathlib import Path
import tempfile
import os
from engine.utils.data_manager import DataManager

@pytest.fixture
def data_manager():
    return DataManager(cache_enabled=True)

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def test_initialization():
    """Test DataManager initialization"""
    manager = DataManager(cache_enabled=True)
    assert manager._cache == {}
    assert manager._cache_enabled == True
    
    manager = DataManager(cache_enabled=False)
    assert manager._cache == {}
    assert manager._cache_enabled == False

def test_load_json(data_manager, temp_dir):
    """Test loading JSON data"""
    test_data = {"name": "test", "value": 42}
    json_file = temp_dir / "test.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f)
    
    loaded_data = data_manager.load(json_file)
    assert loaded_data == test_data
    assert data_manager.get_from_cache(json_file) == test_data

def test_load_yaml(data_manager, temp_dir):
    """Test loading YAML data"""
    test_data = {"name": "test", "value": 42}
    yaml_file = temp_dir / "test.yaml"
    
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(test_data, f)
    
    loaded_data = data_manager.load(yaml_file)
    assert loaded_data == test_data
    assert data_manager.get_from_cache(yaml_file) == test_data

def test_save_json(data_manager, temp_dir):
    """Test saving JSON data"""
    test_data = {"name": "test", "value": 42}
    json_file = temp_dir / "test.json"
    
    data_manager.save(test_data, json_file)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data
    assert data_manager.get_from_cache(json_file) == test_data

def test_save_yaml(data_manager, temp_dir):
    """Test saving YAML data"""
    test_data = {"name": "test", "value": 42}
    yaml_file = temp_dir / "test.yaml"
    
    data_manager.save(test_data, yaml_file)
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        loaded_data = yaml.safe_load(f)
    assert loaded_data == test_data
    assert data_manager.get_from_cache(yaml_file) == test_data

def test_cache_functionality(data_manager, temp_dir):
    """Test cache functionality"""
    test_data = {"name": "test", "value": 42}
    json_file = temp_dir / "test.json"
    
    data_manager.save(test_data, json_file)
    assert data_manager.get_from_cache(json_file) == test_data
    
    data_manager.clear_cache()
    assert data_manager.get_from_cache(json_file) is None

def test_file_not_found(data_manager):
    """Test file not found error"""
    with pytest.raises(FileNotFoundError):
        data_manager.load("nonexistent.json")

def test_invalid_format(data_manager, temp_dir):
    """Test invalid format error"""
    test_file = temp_dir / "test.txt"
    test_file.touch()
    
    with pytest.raises(ValueError):
        data_manager.load(test_file)

def test_json_schema_validation(data_manager):
    """Test JSON schema validation"""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"}
        },
        "required": ["name", "value"]
    }
    
    valid_data = {"name": "test", "value": 42}
    assert data_manager.validate_json_schema(valid_data, schema)
    
    invalid_data = {"name": "test", "value": "not an integer"}
    assert not data_manager.validate_json_schema(invalid_data, schema)

def test_load_save_json_methods(data_manager, temp_dir):
    """Test direct JSON load/save methods"""
    test_data = {"name": "test", "value": 42}
    json_file = str(temp_dir / "test.json")
    
    data_manager.save_json(json_file, test_data)
    loaded_data = data_manager.load_json(json_file)
    assert loaded_data == test_data 