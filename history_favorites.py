# history_favorites.py — Conversion history & saved favorites management

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ConversionRecord:
    """Represents a single conversion in history."""
    timestamp: str
    input_text: str
    output_text: str
    language: str
    conversion_type: str  # 'text_to_braille' or 'braille_to_text'
    notes: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)

class HistoryManager:
    """Manages conversion history with search and filtering."""
    
    def __init__(self, history_file: str = None):
        if history_file is None:
            # Default history location
            app_data = Path.home() / '.braille_converter'
            app_data.mkdir(exist_ok=True)
            history_file = str(app_data / 'history.json')
        
        self.history_file = history_file
        self.history: List[ConversionRecord] = []
        self.max_history_size = 1000  # Keep last 1000 conversions
        
        self._load_history()
    
    def add_conversion(self, input_text: str, output_text: str, 
                      language: str = 'English', 
                      conversion_type: str = 'text_to_braille',
                      notes: str = "") -> ConversionRecord:
        """Add a conversion to history."""
        record = ConversionRecord(
            timestamp=datetime.now().isoformat(),
            input_text=input_text,
            output_text=output_text,
            language=language,
            conversion_type=conversion_type,
            notes=notes
        )
        
        self.history.insert(0, record)  # Most recent first
        
        # Trim if too large
        if len(self.history) > self.max_history_size:
            self.history = self.history[:self.max_history_size]
        
        self._save_history()
        return record
    
    def get_history(self, limit: int = None) -> List[ConversionRecord]:
        """Get conversion history."""
        if limit:
            return self.history[:limit]
        return self.history
    
    def search_history(self, query: str) -> List[ConversionRecord]:
        """Search history by text content."""
        query_lower = query.lower()
        results = []
        
        for record in self.history:
            if (query_lower in record.input_text.lower() or 
                query_lower in record.output_text.lower()):
                results.append(record)
        
        return results
    
    def filter_history(self, conversion_type: str = None, 
                      language: str = None) -> List[ConversionRecord]:
        """Filter history by conversion type or language."""
        results = self.history
        
        if conversion_type:
            results = [r for r in results if r.conversion_type == conversion_type]
        
        if language:
            results = [r for r in results if r.language == language]
        
        return results
    
    def delete_history_item(self, index: int) -> bool:
        """Delete a single history item."""
        try:
            if 0 <= index < len(self.history):
                del self.history[index]
                self._save_history()
                return True
            return False
        except:
            return False
    
    def clear_history(self) -> bool:
        """Clear all history."""
        try:
            self.history = []
            self._save_history()
            return True
        except:
            return False
    
    def get_statistics(self) -> dict:
        """Get history statistics."""
        if not self.history:
            return {'total': 0, 'languages': {}, 'types': {}}
        
        languages = {}
        types = {}
        
        for record in self.history:
            languages[record.language] = languages.get(record.language, 0) + 1
            types[record.conversion_type] = types.get(record.conversion_type, 0) + 1
        
        return {
            'total': len(self.history),
            'languages': languages,
            'types': types,
        }
    
    def _load_history(self):
        """Load history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [ConversionRecord(**item) for item in data]
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save history to file."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                data = [record.to_dict() for record in self.history]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

class FavoritesManager:
    """Manages saved favorite conversions and snippets."""
    
    def __init__(self, favorites_file: str = None):
        if favorites_file is None:
            app_data = Path.home() / '.braille_converter'
            app_data.mkdir(exist_ok=True)
            favorites_file = str(app_data / 'favorites.json')
        
        self.favorites_file = favorites_file
        self.favorites: Dict[str, dict] = {}
        
        self._load_favorites()
    
    def add_favorite(self, name: str, text: str, braille: str, 
                    tags: List[str] = None) -> bool:
        """Add a favorite conversion pair."""
        try:
            self.favorites[name] = {
                'text': text,
                'braille': braille,
                'tags': tags or [],
                'created': datetime.now().isoformat(),
            }
            self._save_favorites()
            return True
        except:
            return False
    
    def get_favorite(self, name: str) -> Optional[dict]:
        """Get a specific favorite."""
        return self.favorites.get(name)
    
    def get_all_favorites(self) -> List[Tuple[str, dict]]:
        """Get all favorites as (name, data) pairs."""
        return list(self.favorites.items())
    
    def search_favorites(self, query: str) -> List[Tuple[str, dict]]:
        """Search favorites by name or tags."""
        query_lower = query.lower()
        results = []
        
        for name, data in self.favorites.items():
            if (query_lower in name.lower() or 
                any(query_lower in tag.lower() for tag in data['tags'])):
                results.append((name, data))
        
        return results
    
    def delete_favorite(self, name: str) -> bool:
        """Delete a favorite."""
        try:
            if name in self.favorites:
                del self.favorites[name]
                self._save_favorites()
                return True
            return False
        except:
            return False
    
    def rename_favorite(self, old_name: str, new_name: str) -> bool:
        """Rename a favorite."""
        try:
            if old_name in self.favorites and new_name not in self.favorites:
                self.favorites[new_name] = self.favorites.pop(old_name)
                self._save_favorites()
                return True
            return False
        except:
            return False
    
    def export_favorites(self, file_path: str) -> bool:
        """Export favorites to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def import_favorites(self, file_path: str) -> Tuple[bool, int]:
        """Import favorites from JSON file. Returns (success, count_imported)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Merge with existing (new ones take precedence)
            self.favorites.update(imported)
            self._save_favorites()
            
            return True, len(imported)
        except Exception as e:
            print(f"Import error: {e}")
            return False, 0
    
    def get_statistics(self) -> dict:
        """Get favorites statistics."""
        all_tags = set()
        for fav in self.favorites.values():
            all_tags.update(fav['tags'])
        
        return {
            'total_favorites': len(self.favorites),
            'unique_tags': len(all_tags),
            'all_tags': list(all_tags),
        }
    
    def _load_favorites(self):
        """Load favorites from file."""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            self.favorites = {}
    
    def _save_favorites(self):
        """Save favorites to file."""
        try:
            os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving favorites: {e}")

# Global instances
history_manager = HistoryManager()
favorites_manager = FavoritesManager()
