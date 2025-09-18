"""
Database manager for crop yield prediction platform.
Handles PostgreSQL operations for users, farms, predictions, and feedback.
"""

import asyncpg
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from contextlib import asynccontextmanager

from .models import UserCreate, FarmCreate, FeedbackCreate

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for PostgreSQL operations"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 
                                    'postgresql://postgres:postgres@localhost:5432/crop_yield_db')
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        async with self.pool.acquire() as connection:
            yield connection
    
    # User operations
    async def create_user(self, user: UserCreate, db=None) -> int:
        """Create a new user"""
        query = """
        INSERT INTO users (name, phone, location_lat, location_lon, preferred_lang)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        
        if db:
            result = await db.fetchrow(
                query, user.name, user.phone, user.location_lat, 
                user.location_lon, user.preferred_lang
            )
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(
                    query, user.name, user.phone, user.location_lat, 
                    user.location_lon, user.preferred_lang
                )
        
        return result['id']
    
    async def get_user(self, user_id: int, db=None) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = $1"
        
        if db:
            result = await db.fetchrow(query, user_id)
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(query, user_id)
        
        return dict(result) if result else None
    
    # Farm operations
    async def create_farm(self, farm: FarmCreate, db=None) -> int:
        """Create a new farm"""
        query = """
        INSERT INTO farms (user_id, name, area_ha, soil_inputs_json, crop_preferences)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        
        soil_inputs_json = json.dumps(farm.soil_inputs_json) if farm.soil_inputs_json else None
        
        if db:
            result = await db.fetchrow(
                query, farm.user_id, farm.name, farm.area_ha, 
                soil_inputs_json, farm.crop_preferences
            )
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(
                    query, farm.user_id, farm.name, farm.area_ha, 
                    soil_inputs_json, farm.crop_preferences
                )
        
        return result['id']
    
    async def get_farm(self, farm_id: int, db=None) -> Optional[Dict[str, Any]]:
        """Get farm by ID"""
        query = "SELECT * FROM farms WHERE id = $1"
        
        if db:
            result = await db.fetchrow(query, farm_id)
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(query, farm_id)
        
        if result:
            farm_dict = dict(result)
            if farm_dict['soil_inputs_json']:
                farm_dict['soil_inputs_json'] = json.loads(farm_dict['soil_inputs_json'])
            return farm_dict
        
        return None
    
    async def get_user_farms(self, user_id: int, db=None) -> List[Dict[str, Any]]:
        """Get all farms for a user"""
        query = "SELECT * FROM farms WHERE user_id = $1 ORDER BY created_at DESC"
        
        if db:
            results = await db.fetch(query, user_id)
        else:
            async with self.get_connection() as conn:
                results = await conn.fetch(query, user_id)
        
        farms = []
        for result in results:
            farm_dict = dict(result)
            if farm_dict['soil_inputs_json']:
                farm_dict['soil_inputs_json'] = json.loads(farm_dict['soil_inputs_json'])
            farms.append(farm_dict)
        
        return farms
    
    # Prediction operations
    async def store_prediction(self, request_data: dict, response_data: dict, db=None):
        """Store prediction in database"""
        query = """
        INSERT INTO predictions (farm_id, input_json, result_json, model_version, 
                               confidence_score, predicted_yield_t_ha)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
        """
        
        # Extract values from response
        model_version = response_data.get('model_version', 'unknown')
        confidence_score = response_data.get('confidence_score', 0.0)
        predicted_yield = response_data.get('predicted_yield_t_ha', 0.0)
        
        # Use farm_id if available, otherwise None
        farm_id = request_data.get('farm_id')
        
        if db:
            result = await db.fetchrow(
                query, farm_id, json.dumps(request_data), json.dumps(response_data),
                model_version, confidence_score, predicted_yield
            )
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(
                    query, farm_id, json.dumps(request_data), json.dumps(response_data),
                    model_version, confidence_score, predicted_yield
                )
        
        return result['id']
    
    # Feedback operations
    async def create_feedback(self, feedback: FeedbackCreate, db=None) -> int:
        """Create feedback for a prediction"""
        query = """
        INSERT INTO feedback (prediction_id, actual_yield_t_ha, comment, rating)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """
        
        if db:
            result = await db.fetchrow(
                query, feedback.prediction_id, feedback.actual_yield_t_ha,
                feedback.comment, feedback.rating
            )
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(
                    query, feedback.prediction_id, feedback.actual_yield_t_ha,
                    feedback.comment, feedback.rating
                )
        
        return result['id']
    
    async def get_prediction_feedback(self, prediction_id: int, db=None) -> List[Dict[str, Any]]:
        """Get feedback for a prediction"""
        query = "SELECT * FROM feedback WHERE prediction_id = $1 ORDER BY timestamp DESC"
        
        if db:
            results = await db.fetch(query, prediction_id)
        else:
            async with self.get_connection() as conn:
                results = await conn.fetch(query, prediction_id)
        
        return [dict(result) for result in results]
    
    # Analytics operations
    async def get_prediction_analytics(self, user_id: Optional[int] = None,
                                     farm_id: Optional[int] = None,
                                     days: int = 30, db=None) -> Dict[str, Any]:
        """Get prediction analytics"""
        base_query = """
        SELECT 
            COUNT(*) as total_predictions,
            AVG(predicted_yield_t_ha) as avg_predicted_yield,
            AVG(confidence_score) as avg_confidence,
            MIN(created_at) as first_prediction,
            MAX(created_at) as last_prediction
        FROM predictions p
        """
        
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            conditions.append(f"p.farm_id IN (SELECT id FROM farms WHERE user_id = ${param_count + 1})")
            params.append(user_id)
            param_count += 1
        
        if farm_id:
            conditions.append(f"p.farm_id = ${param_count + 1}")
            params.append(farm_id)
            param_count += 1
        
        # Add time filter
        conditions.append(f"p.created_at >= ${param_count + 1}")
        params.append(datetime.now() - timedelta(days=days))
        param_count += 1
        
        if conditions:
            query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            query = base_query
        
        if db:
            result = await db.fetchrow(query, *params)
        else:
            async with self.get_connection() as conn:
                result = await conn.fetchrow(query, *params)
        
        analytics = dict(result) if result else {}
        
        # Get feedback statistics
        feedback_query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(actual_yield_t_ha) as avg_actual_yield,
            AVG(rating) as avg_rating
        FROM feedback f
        JOIN predictions p ON f.prediction_id = p.id
        WHERE p.created_at >= $1
        """
        
        feedback_params = [datetime.now() - timedelta(days=days)]
        
        if user_id:
            feedback_query += " AND p.farm_id IN (SELECT id FROM farms WHERE user_id = $2)"
            feedback_params.append(user_id)
        elif farm_id:
            feedback_query += " AND p.farm_id = $2"
            feedback_params.append(farm_id)
        
        if db:
            feedback_result = await db.fetchrow(feedback_query, *feedback_params)
        else:
            async with self.get_connection() as conn:
                feedback_result = await conn.fetchrow(feedback_query, *feedback_params)
        
        if feedback_result:
            analytics.update(dict(feedback_result))
        
        return analytics

# Dependency for FastAPI
async def get_db():
    """Dependency to get database connection"""
    # This would be injected by the FastAPI app
    # For now, return None as the DatabaseManager handles connections internally
    return None
