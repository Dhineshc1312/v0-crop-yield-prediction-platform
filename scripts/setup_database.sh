#!/bin/bash

# Database setup script for SIH AI Harvesters Platform
# This script initializes the PostgreSQL database and runs migrations

set -e

echo "🌾 Setting up SIH AI Harvesters Database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Create database if it doesn't exist
echo "Creating database if it doesn't exist..."
psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'sih_ai_harvesters'" | grep -q 1 || psql -h localhost -U postgres -c "CREATE DATABASE sih_ai_harvesters"

# Run initialization script
echo "Running database initialization..."
psql -h localhost -U postgres -d sih_ai_harvesters -f /scripts/init_db.sql

# Seed sample data
echo "Seeding sample data..."
psql -h localhost -U postgres -d sih_ai_harvesters -f /scripts/seed_data.sql

echo "✅ Database setup complete!"
