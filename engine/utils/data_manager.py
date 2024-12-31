import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging

class DataManager:
    def __init__(self, cache_enabled: bool = True):
        self._cache: Dict[str, Any] = {}
        self._cache_enabled = cache_enabled
        self.logger = logging.getLogger(__name__)

    def load(self, file_path: Union[str, Path], format: str = "auto") -> Any:
        """Belirtilen dosyadan veriyi yükler.
        
        Args:
            file_path: Yüklenecek dosyanın yolu
            format: Dosya formatı ('json', 'yaml' veya 'auto')
            
        Returns:
            Yüklenen veri
        """
        file_path = Path(file_path)
        
        if self._cache_enabled and str(file_path) in self._cache:
            return self._cache[str(file_path)]
            
        if not file_path.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
            
        if format == "auto":
            format = file_path.suffix.lower()[1:]
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if format == "json":
                    data = json.load(f)
                elif format == "yaml" or format == "yml":
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Desteklenmeyen format: {format}")
                    
            if self._cache_enabled:
                self._cache[str(file_path)] = data
                
            return data
            
        except Exception as e:
            self.logger.error(f"Veri yükleme hatası: {e}")
            raise

    def save(self, data: Any, file_path: Union[str, Path], format: str = "auto") -> None:
        """Veriyi belirtilen dosyaya kaydeder.
        
        Args:
            data: Kaydedilecek veri
            file_path: Kaydedilecek dosya yolu
            format: Dosya formatı ('json', 'yaml' veya 'auto')
        """
        file_path = Path(file_path)
        
        if format == "auto":
            format = file_path.suffix.lower()[1:]
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == "json":
                    json.dump(data, f, indent=4, ensure_ascii=False)
                elif format == "yaml" or format == "yml":
                    yaml.safe_dump(data, f, allow_unicode=True)
                else:
                    raise ValueError(f"Desteklenmeyen format: {format}")
                    
            if self._cache_enabled:
                self._cache[str(file_path)] = data
                
        except Exception as e:
            self.logger.error(f"Veri kaydetme hatası: {e}")
            raise

    def clear_cache(self) -> None:
        """Önbelleği temizler."""
        self._cache.clear()

    def get_from_cache(self, file_path: Union[str, Path]) -> Optional[Any]:
        """Önbellekten veri getirir.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Önbellekteki veri veya None
        """
        return self._cache.get(str(file_path))

    def validate_json_schema(self, data: Any, schema: Dict) -> bool:
        """JSON şemasına göre veriyi doğrular.
        
        Args:
            data: Doğrulanacak veri
            schema: JSON şeması
            
        Returns:
            Doğrulama sonucu
        """
        try:
            from jsonschema import validate
            validate(instance=data, schema=schema)
            return True
        except Exception as e:
            self.logger.error(f"Şema doğrulama hatası: {e}")
            return False 