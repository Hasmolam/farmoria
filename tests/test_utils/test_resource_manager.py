import pytest
import json
import os
from engine.utils.data_manager import DataManager

class TestDataManager:
    """DataManager test sınıfı"""
    
    @pytest.fixture
    def data_manager(self):
        """DataManager fixture'ı"""
        return DataManager()
        
    def test_save_json(self, data_manager, tmp_path):
        """JSON kaydetme testi"""
        test_data = {"test": "data"}
        file_path = tmp_path / "test.json"
        data_manager.save_json(str(file_path), test_data)
        assert file_path.exists()
        
    def test_load_json(self, data_manager, tmp_path):
        """JSON yükleme testi"""
        test_data = {"test": "data"}
        file_path = tmp_path / "test.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        loaded_data = data_manager.load_json(str(file_path))
        assert loaded_data == test_data
        
    def test_save_load_nested_data(self, data_manager, tmp_path):
        """İç içe veri kaydetme/yükleme testi"""
        test_data = {
            "level1": {
                "level2": {
                    "value": 42
                }
            }
        }
        file_path = tmp_path / "nested.json"
        data_manager.save_json(str(file_path), test_data)
        loaded_data = data_manager.load_json(str(file_path))
        assert loaded_data == test_data
        
    def test_save_load_special_characters(self, data_manager, tmp_path):
        """Özel karakterli veri kaydetme/yükleme testi"""
        test_data = {
            "türkçe": "çğıöşü",
            "symbols": "!@#$%^&*()"
        }
        file_path = tmp_path / "special.json"
        data_manager.save_json(str(file_path), test_data)
        loaded_data = data_manager.load_json(str(file_path))
        assert loaded_data == test_data
        
    def test_file_not_found(self, data_manager):
        """Olmayan dosya testi"""
        with pytest.raises(FileNotFoundError):
            data_manager.load_json("nonexistent.json")
            
    def test_invalid_json(self, data_manager, tmp_path):
        """Geçersiz JSON testi"""
        file_path = tmp_path / "invalid.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        with pytest.raises(json.JSONDecodeError):
            data_manager.load_json(str(file_path)) 