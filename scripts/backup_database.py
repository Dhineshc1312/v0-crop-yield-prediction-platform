#!/usr/bin/env python3
"""
Database backup script for SIH AI Harvesters Platform
Creates automated backups with compression and retention management
"""

import os
import sys
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, database_url: str, backup_dir: str = "./backups"):
        self.database_url = database_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Parse database URL
        self.parse_database_url()
    
    def parse_database_url(self):
        """Parse PostgreSQL connection details from URL"""
        # Simple URL parsing for postgresql://user:pass@host:port/dbname
        url = self.database_url.replace('postgresql://', '')
        
        if '@' in url:
            auth, host_db = url.split('@', 1)
            if ':' in auth:
                self.db_user, self.db_password = auth.split(':', 1)
            else:
                self.db_user = auth
                self.db_password = ''
        else:
            host_db = url
            self.db_user = 'postgres'
            self.db_password = ''
        
        if '/' in host_db:
            host_port, self.db_name = host_db.split('/', 1)
        else:
            host_port = host_db
            self.db_name = 'sih_ai_harvesters'
        
        if ':' in host_port:
            self.db_host, self.db_port = host_port.split(':', 1)
        else:
            self.db_host = host_port
            self.db_port = '5432'
    
    def create_backup(self, compress: bool = True):
        """Create a database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sih_ai_harvesters_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Set environment variables for pg_dump
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            # Create pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '--verbose',
                '--clean',
                '--if-exists',
                '--create',
                '-f', str(backup_path)
            ]
            
            logger.info(f"Creating backup: {backup_filename}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return None
            
            logger.info(f"✅ Backup created: {backup_path}")
            
            # Compress backup if requested
            if compress:
                compressed_path = self.compress_backup(backup_path)
                backup_path.unlink()  # Remove uncompressed file
                backup_path = compressed_path
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def compress_backup(self, backup_path: Path):
        """Compress backup file using gzip"""
        compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"✅ Backup compressed: {compressed_path}")
        return compressed_path
    
    def restore_backup(self, backup_path: Path):
        """Restore database from backup"""
        try:
            # Decompress if needed
            if backup_path.suffix == '.gz':
                temp_path = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
            
            # Set environment variables
            env = os.environ.copy()
            if self.db_password:
                env['PGPASSWORD'] = self.db_password
            
            # Create psql command
            cmd = [
                'psql',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-f', str(backup_path)
            ]
            
            logger.info(f"Restoring backup: {backup_path}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Restore failed: {result.stderr}")
                return False
            
            logger.info("✅ Backup restored successfully")
            
            # Clean up temporary file if created
            if backup_path.suffix != '.gz' and str(backup_path).endswith('.sql'):
                backup_path.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        removed_count = 0
        for backup_file in self.backup_dir.glob("sih_ai_harvesters_backup_*.sql*"):
            # Extract timestamp from filename
            try:
                timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                if backup_file.suffix == '.gz':
                    timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if file_date < cutoff_date:
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_file}")
                    
            except (ValueError, IndexError):
                logger.warning(f"Could not parse date from filename: {backup_file}")
        
        logger.info(f"✅ Cleaned up {removed_count} old backups")
    
    def list_backups(self):
        """List all available backups"""
        backups = sorted(self.backup_dir.glob("sih_ai_harvesters_backup_*.sql*"))
        
        if not backups:
            logger.info("No backups found")
            return []
        
        logger.info("Available backups:")
        for backup in backups:
            size = backup.stat().st_size
            size_mb = size / (1024 * 1024)
            logger.info(f"  {backup.name} ({size_mb:.1f} MB)")
        
        return backups

def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is required")
        sys.exit(1)
    
    backup_manager = DatabaseBackup(database_url)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            backup_path = backup_manager.create_backup()
            if backup_path:
                logger.info(f"Backup created successfully: {backup_path}")
            else:
                sys.exit(1)
        
        elif command == "restore":
            if len(sys.argv) < 3:
                logger.error("Usage: python backup_database.py restore <backup_file>")
                sys.exit(1)
            
            backup_file = Path(sys.argv[2])
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                sys.exit(1)
            
            success = backup_manager.restore_backup(backup_file)
            if not success:
                sys.exit(1)
        
        elif command == "list":
            backup_manager.list_backups()
        
        elif command == "cleanup":
            retention_days = 30
            if len(sys.argv) > 2:
                retention_days = int(sys.argv[2])
            
            backup_manager.cleanup_old_backups(retention_days)
        
        else:
            logger.error("Unknown command. Use 'create', 'restore', 'list', or 'cleanup'")
            sys.exit(1)
    
    else:
        # Default action is to create backup
        backup_path = backup_manager.create_backup()
        if backup_path:
            logger.info(f"Backup created successfully: {backup_path}")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
