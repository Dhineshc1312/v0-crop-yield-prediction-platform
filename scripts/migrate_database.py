#!/usr/bin/env python3
"""
Database migration script for SIH AI Harvesters Platform
Handles database schema updates and data migrations
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
    
    async def create_migrations_table(self, conn):
        """Create migrations tracking table if it doesn't exist"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(64)
            )
        """)
        logger.info("✅ Migrations table ready")
    
    async def get_applied_migrations(self, conn):
        """Get list of already applied migrations"""
        rows = await conn.fetch("SELECT migration_name FROM schema_migrations ORDER BY applied_at")
        return [row['migration_name'] for row in rows]
    
    async def apply_migration(self, conn, migration_file: Path):
        """Apply a single migration file"""
        migration_name = migration_file.stem
        
        try:
            # Read migration content
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.md5(migration_sql.encode()).hexdigest()
            
            # Execute migration in transaction
            async with conn.transaction():
                await conn.execute(migration_sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (migration_name, checksum) VALUES ($1, $2)",
                    migration_name, checksum
                )
            
            logger.info(f"✅ Applied migration: {migration_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration_name}: {e}")
            raise
    
    async def run_migrations(self):
        """Run all pending migrations"""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            await self.create_migrations_table(conn)
            applied_migrations = await self.get_applied_migrations(conn)
            
            # Find migration files
            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            
            if not migration_files:
                logger.info("No migration files found")
                return
            
            pending_migrations = [
                f for f in migration_files 
                if f.stem not in applied_migrations
            ]
            
            if not pending_migrations:
                logger.info("All migrations are up to date")
                return
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            for migration_file in pending_migrations:
                await self.apply_migration(conn, migration_file)
            
            logger.info("🎉 All migrations completed successfully!")
            
        finally:
            await conn.close()
    
    def create_migration(self, name: str):
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        filepath = self.migrations_dir / filename
        
        template = f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}
-- Description: Add your migration description here

-- Add your SQL statements here
-- Example:
-- ALTER TABLE users ADD COLUMN new_field VARCHAR(255);

-- Remember to add rollback instructions in comments:
-- Rollback: ALTER TABLE users DROP COLUMN new_field;
"""
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        logger.info(f"✅ Created migration file: {filepath}")
        return filepath

async def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is required")
        sys.exit(1)
    
    migrator = DatabaseMigrator(database_url)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            if len(sys.argv) < 3:
                logger.error("Usage: python migrate_database.py create <migration_name>")
                sys.exit(1)
            
            migration_name = sys.argv[2]
            migrator.create_migration(migration_name)
        
        elif command == "migrate":
            await migrator.run_migrations()
        
        else:
            logger.error("Unknown command. Use 'create' or 'migrate'")
            sys.exit(1)
    
    else:
        # Default action is to run migrations
        await migrator.run_migrations()

if __name__ == "__main__":
    asyncio.run(main())
