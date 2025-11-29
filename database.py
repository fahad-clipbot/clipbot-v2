"""
Database module for ClipBot V2
Handles users, subscriptions, and download statistics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "/tmp/clipbot.db"):

    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                preferred_language TEXT DEFAULT 'ar',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tier TEXT NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                payment_id TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Downloads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                platform TEXT NOT NULL,
                media_type TEXT NOT NULL,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_downloads INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                new_users INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    # User management
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language_code: str = None, preferred_language: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, language_code, preferred_language)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                language_code = excluded.language_code,
                preferred_language = COALESCE(excluded.preferred_language, users.preferred_language),
                last_active = CURRENT_TIMESTAMP
        """, (user_id, username, first_name, last_name, language_code, preferred_language))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def set_user_language(self, user_id: int, language: str):
        """Set user's preferred language"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET preferred_language = ? WHERE user_id = ?
        """, (language, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        user = self.get_user(user_id)
        if user and user.get('preferred_language'):
            return user['preferred_language']
        return 'ar'  # Default to Arabic
    
    # Subscription management
    def add_subscription(self, user_id: int, tier: str, duration_days: int = 30, 
                        payment_id: str = None):
        """Add subscription for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now() + timedelta(days=duration_days)
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, tier, end_date, payment_id, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (user_id, tier, end_date, payment_id))
        
        conn.commit()
        conn.close()
    
    def get_active_subscription(self, user_id: int) -> Optional[Dict]:
        """Get active subscription for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND status = 'active' AND end_date > CURRENT_TIMESTAMP
            ORDER BY end_date DESC LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_subscriptions(self) -> List[Dict]:
        """Get all subscriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, u.username, u.first_name 
            FROM subscriptions s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.start_date DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def expire_subscriptions(self):
        """Mark expired subscriptions as expired"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE subscriptions 
            SET status = 'expired' 
            WHERE status = 'active' AND end_date <= CURRENT_TIMESTAMP
        """)
        
        conn.commit()
        conn.close()
    
    # Download management
    def add_download(self, user_id: int, url: str, platform: str, 
                    media_type: str, success: bool = True):
        """Record a download"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO downloads (user_id, url, platform, media_type, success)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, url, platform, media_type, success))
        
        conn.commit()
        conn.close()
    
    def get_user_downloads_today(self, user_id: int) -> int:
        """Get number of downloads by user today"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM downloads 
            WHERE user_id = ? AND date(download_date) = date('now') AND success = 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['count'] if row else 0
    
    def get_downloads_by_date(self, days: int = 7) -> List[Dict]:
        """Get downloads grouped by date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                date(download_date) as date,
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                COUNT(DISTINCT user_id) as unique_users
            FROM downloads
            WHERE download_date >= datetime('now', '-' || ? || ' days')
            GROUP BY date(download_date)
            ORDER BY date DESC
        """, (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_downloads_by_platform(self) -> List[Dict]:
        """Get downloads grouped by platform"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                platform,
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
            FROM downloads
            GROUP BY platform
            ORDER BY total DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_downloads_by_type(self) -> List[Dict]:
        """Get downloads grouped by media type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                media_type,
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
            FROM downloads
            GROUP BY media_type
            ORDER BY total DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Statistics
    def get_total_stats(self) -> Dict:
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Total downloads
        cursor.execute("SELECT COUNT(*) as count FROM downloads WHERE success = 1")
        total_downloads = cursor.fetchone()['count']
        
        # Active subscriptions
        cursor.execute("""
            SELECT COUNT(*) as count FROM subscriptions 
            WHERE status = 'active' AND end_date > CURRENT_TIMESTAMP
        """)
        active_subs = cursor.fetchone()['count']
        
        # Today's stats
        cursor.execute("""
            SELECT COUNT(*) as count FROM downloads 
            WHERE date(download_date) = date('now') AND success = 1
        """)
        today_downloads = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM downloads 
            WHERE date(download_date) = date('now')
        """)
        today_active_users = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_downloads': total_downloads,
            'active_subscriptions': active_subs,
            'today_downloads': today_downloads,
            'today_active_users': today_active_users
        }

    # Admin functions
    def get_admin_stats(self) -> Dict:
        """Get admin dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Active subscriptions
        cursor.execute("""
            SELECT COUNT(*) as count FROM subscriptions 
            WHERE status = 'active' AND end_date > CURRENT_TIMESTAMP
        """)
        active_subscriptions = cursor.fetchone()['count']
        
        # Downloads today
        cursor.execute("""
            SELECT COUNT(*) as count FROM downloads 
            WHERE date(download_date) = date('now') AND success = 1
        """)
        downloads_today = cursor.fetchone()['count']
        
        # Downloads this week
        cursor.execute("""
            SELECT COUNT(*) as count FROM downloads 
            WHERE download_date >= date('now', '-7 days') AND success = 1
        """)
        downloads_week = cursor.fetchone()['count']
        
        # Downloads this month
        cursor.execute("""
            SELECT COUNT(*) as count FROM downloads 
            WHERE download_date >= date('now', '-30 days') AND success = 1
        """)
        downloads_month = cursor.fetchone()['count']
        
        # Total downloads
        cursor.execute("SELECT COUNT(*) as count FROM downloads WHERE success = 1")
        total_downloads = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions,
            'downloads_today': downloads_today,
            'downloads_week': downloads_week,
            'downloads_month': downloads_month,
            'total_downloads': total_downloads
        }
    
    def get_active_subscriptions(self) -> List[Dict]:
        """Get all active subscriptions with user info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, u.username, u.first_name, u.last_name
            FROM subscriptions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.status = 'active' AND s.end_date > CURRENT_TIMESTAMP
            ORDER BY s.end_date DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            sub_dict = dict(row)
            # Convert timestamp strings to datetime objects if needed
            if 'end_date' in sub_dict and sub_dict['end_date']:
                try:
                    sub_dict['expiry_date'] = datetime.fromisoformat(sub_dict['end_date'])
                except:
                    pass
            result.append(sub_dict)
        
        return result
    
    def get_download_stats(self, days: int = 7) -> List[Dict]:
        """Get download statistics for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                date(download_date) as date,
                COUNT(*) as count
            FROM downloads
            WHERE download_date >= date('now', ? || ' days') AND success = 1
            GROUP BY date(download_date)
            ORDER BY date DESC
        """, (f'-{days}',))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
11
