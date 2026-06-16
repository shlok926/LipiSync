"""
Statistics Dashboard Module - Track user activity and usage analytics

Tracks:
- Total conversions count
- Language distribution
- Average input length
- Time spent in app
- Most used features
- Daily/weekly/monthly trends
- Export reports (PDF/CSV)
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from collections import defaultdict


class StatisticsTracker:
    """Track application statistics and usage analytics."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize statistics tracker.
        
        Args:
            db_path: Path to SQLite database (default: ~/.braille_converter/stats.db)
        """
        if db_path is None:
            config_dir = Path.home() / ".braille_converter"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "statistics.db")
        
        self.db_path = db_path
        self.connection = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize or connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create conversions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    feature TEXT,
                    input_language TEXT,
                    output_language TEXT,
                    input_length INTEGER,
                    output_length INTEGER,
                    duration_ms INTEGER,
                    status TEXT DEFAULT 'success'
                )
            """)
            
            # Create features table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    feature_name TEXT,
                    count INTEGER DEFAULT 1
                )
            """)
            
            # Create session table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_start DATETIME,
                    session_end DATETIME,
                    duration_minutes INTEGER,
                    conversions_count INTEGER
                )
            """)
            
            self.connection.commit()
        
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    def log_conversion(
        self,
        feature: str,
        input_language: str,
        output_language: str,
        input_length: int,
        output_length: int,
        duration_ms: int = 0,
        status: str = "success"
    ) -> bool:
        """
        Log a conversion event.
        
        Args:
            feature: Feature name (e.g., 'text_to_braille')
            input_language: Input language
            output_language: Output language
            input_length: Length of input text
            output_length: Length of output text
            duration_ms: Processing duration in milliseconds
            status: Conversion status
        
        Returns:
            Success status
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO conversions 
                (feature, input_language, output_language, input_length, output_length, duration_ms, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (feature, input_language, output_language, input_length, output_length, duration_ms, status))
            
            self.connection.commit()
            return True
        
        except Exception as e:
            print(f"❌ Error logging conversion: {e}")
            return False
    
    def log_feature_usage(self, feature_name: str) -> bool:
        """Log feature usage."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO feature_usage (feature_name) VALUES (?)
            """, (feature_name,))
            
            self.connection.commit()
            return True
        
        except Exception as e:
            print(f"❌ Error logging feature usage: {e}")
            return False
    
    def start_session(self) -> int:
        """Start a new session. Returns session ID."""
        self.session_start = datetime.now()
        return int(self.session_start.timestamp())
    
    def end_session(self, session_id: int, conversions_count: int = 0) -> bool:
        """End a session."""
        try:
            session_end = datetime.now()
            duration_minutes = int((session_end - self.session_start).total_seconds() / 60)
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_start, session_end, duration_minutes, conversions_count)
                VALUES (?, ?, ?, ?)
            """, (self.session_start.isoformat(), session_end.isoformat(), duration_minutes, conversions_count))
            
            self.connection.commit()
            return True
        
        except Exception as e:
            print(f"❌ Error ending session: {e}")
            return False
    
    def get_total_conversions(self) -> int:
        """Get total number of conversions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversions WHERE status = 'success'")
            count = cursor.fetchone()[0]
            return count
        except:
            return 0
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of conversions by language pair."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT input_language, output_language, COUNT(*) as count
                FROM conversions
                WHERE status = 'success'
                GROUP BY input_language, output_language
            """)
            
            distribution = defaultdict(int)
            for input_lang, output_lang, count in cursor.fetchall():
                key = f"{input_lang} → {output_lang}"
                distribution[key] = count
            
            return dict(distribution)
        except:
            return {}
    
    def get_most_used_features(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most used features."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT feature, COUNT(*) as count
                FROM conversions
                WHERE status = 'success'
                GROUP BY feature
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            
            return cursor.fetchall()
        except:
            return []
    
    def get_feature_usage_stats(self) -> Dict[str, int]:
        """Get feature usage statistics."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT feature_name, COUNT(*) as count
                FROM feature_usage
                GROUP BY feature_name
                ORDER BY count DESC
            """)
            
            stats = {}
            for feature, count in cursor.fetchall():
                stats[feature] = count
            
            return stats
        except:
            return {}
    
    def get_average_input_length(self) -> float:
        """Get average input length across all conversions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT AVG(input_length) FROM conversions WHERE status = 'success'
            """)
            
            result = cursor.fetchone()[0]
            return round(result, 2) if result else 0
        except:
            return 0
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """Get stats for last N days."""
        try:
            cursor = self.connection.cursor()
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM conversions
                WHERE timestamp > ? AND status = 'success'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (cutoff_date,))
            
            stats = {}
            for date, count in cursor.fetchall():
                stats[date] = {"conversions": count}
            
            return stats
        except:
            return {}
    
    def get_average_processing_time(self) -> float:
        """Get average processing time in milliseconds."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT AVG(duration_ms) FROM conversions 
                WHERE status = 'success' AND duration_ms > 0
            """)
            
            result = cursor.fetchone()[0]
            return round(result, 2) if result else 0
        except:
            return 0
    
    def get_success_rate(self) -> float:
        """Get conversion success rate (0-100%)."""
        try:
            cursor = self.connection.cursor()
            
            # Total conversions
            cursor.execute("SELECT COUNT(*) FROM conversions")
            total = cursor.fetchone()[0]
            
            if total == 0:
                return 100.0
            
            # Successful conversions
            cursor.execute("SELECT COUNT(*) FROM conversions WHERE status = 'success'")
            successful = cursor.fetchone()[0]
            
            rate = (successful / total) * 100
            return round(rate, 2)
        except:
            return 0
    
    def get_total_time_spent(self) -> Dict[str, int]:
        """Get total time spent in app."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT SUM(duration_minutes) as total_minutes, COUNT(*) as sessions
                FROM sessions
            """)
            
            total_minutes, sessions = cursor.fetchone()
            total_minutes = total_minutes or 0
            
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            return {
                "total_minutes": int(total_minutes),
                "total_hours": int(hours),
                "remaining_minutes": int(minutes),
                "sessions": int(sessions) if sessions else 0
            }
        except:
            return {"total_minutes": 0, "total_hours": 0, "remaining_minutes": 0, "sessions": 0}
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics summary."""
        return {
            "total_conversions": self.get_total_conversions(),
            "average_input_length": self.get_average_input_length(),
            "average_processing_time_ms": self.get_average_processing_time(),
            "success_rate_percent": self.get_success_rate(),
            "language_distribution": self.get_language_distribution(),
            "most_used_features": dict(self.get_most_used_features()),
            "feature_usage": self.get_feature_usage_stats(),
            "daily_stats_7days": self.get_daily_stats(7),
            "total_time_spent": self.get_total_time_spent(),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_to_json(self, export_path: str) -> Tuple[bool, str]:
        """Export statistics to JSON file."""
        try:
            stats = self.get_comprehensive_stats()
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
            
            return True, f"✅ Statistics exported to {export_path}"
        except Exception as e:
            return False, f"❌ Export failed: {str(e)}"
    
    def export_to_csv(self, export_path: str) -> Tuple[bool, str]:
        """Export conversion history to CSV file."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT timestamp, feature, input_language, output_language, 
                       input_length, output_length, duration_ms, status
                FROM conversions
                ORDER BY timestamp DESC
            """)
            
            rows = cursor.fetchall()
            
            with open(export_path, 'w', encoding='utf-8', newline='') as f:
                f.write("Timestamp,Feature,Input Language,Output Language,")
                f.write("Input Length,Output Length,Duration (ms),Status\n")
                
                for row in rows:
                    f.write(','.join(str(x) for x in row) + '\n')
            
            return True, f"✅ Conversion history exported to {export_path}"
        except Exception as e:
            return False, f"❌ Export failed: {str(e)}"
    
    def clear_statistics(self, days_old: int = 0) -> Tuple[bool, str]:
        """
        Clear old statistics.
        
        Args:
            days_old: Clear records older than N days (0 = clear all)
        
        Returns:
            (success, message)
        """
        try:
            cursor = self.connection.cursor()
            
            if days_old == 0:
                cursor.execute("DELETE FROM conversions")
                cursor.execute("DELETE FROM sessions")
                cursor.execute("DELETE FROM feature_usage")
                message = "✅ All statistics cleared"
            else:
                cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
                cursor.execute("DELETE FROM conversions WHERE timestamp < ?", (cutoff_date,))
                cursor.execute("DELETE FROM sessions WHERE session_start < ?", (cutoff_date,))
                message = f"✅ Statistics older than {days_old} days cleared"
            
            self.connection.commit()
            return True, message
        
        except Exception as e:
            return False, f"❌ Clear failed: {str(e)}"
    
    def get_status(self) -> Dict:
        """Get tracker status."""
        return {
            "database_path": self.db_path,
            "database_exists": Path(self.db_path).exists(),
            "status": "✅ Ready",
            "total_conversions": self.get_total_conversions()
        }
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


# Global instance
statistics_tracker = StatisticsTracker()

def log_conversion(feature: str, input_language: str, output_language: str, input_length: int, output_length: int, duration_ms: int = 0, status: str = "success") -> bool:
    """Module-level wrapper for log_conversion."""
    return statistics_tracker.log_conversion(
        feature=feature,
        input_language=input_language,
        output_language=output_language,
        input_length=input_length,
        output_length=output_length,
        duration_ms=duration_ms,
        status=status
    )

def get_comprehensive_stats() -> Dict:
    """Module-level wrapper for get_comprehensive_stats."""
    return statistics_tracker.get_comprehensive_stats()

def export_to_json(export_path: str) -> Tuple[bool, str]:
    """Module-level wrapper for export_to_json."""
    return statistics_tracker.export_to_json(export_path)

def export_to_csv(export_path: str) -> Tuple[bool, str]:
    """Module-level wrapper for export_to_csv."""
    return statistics_tracker.export_to_csv(export_path)


if __name__ == "__main__":
    print("=" * 70)
    print("STATISTICS DASHBOARD MODULE")
    print("=" * 70)
    print()
    
    tracker = StatisticsTracker()
    
    print("✅ Statistics tracker initialized")
    print(f"Database: {tracker.db_path}")
    print()
    
    # Log some test conversions
    print("Logging test conversions...")
    for i in range(5):
        tracker.log_conversion(
            feature="text_to_braille",
            input_language="English",
            output_language="Braille",
            input_length=100 + (i * 50),
            output_length=100 + (i * 50),
            duration_ms=50 + (i * 10)
        )
    
    tracker.log_feature_usage("converter")
    tracker.log_feature_usage("converter")
    tracker.log_feature_usage("speech")
    
    print()
    
    # Get statistics
    stats = tracker.get_comprehensive_stats()
    print("Statistics Summary:")
    print(f"  Total conversions: {stats['total_conversions']}")
    print(f"  Average input length: {stats['average_input_length']} chars")
    print(f"  Average processing time: {stats['average_processing_time_ms']} ms")
    print(f"  Success rate: {stats['success_rate_percent']}%")
    print()
    
    print("=" * 70)
    print("✅ Statistics Dashboard Module Ready!")
    print("=" * 70)
    
    tracker.close()
