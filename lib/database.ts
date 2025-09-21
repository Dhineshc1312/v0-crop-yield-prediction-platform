import { Pool } from 'pg'

// Database connection pool
let pool: Pool | null = null

function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/crop_yield_db',
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
    })
  }
  return pool
}

export interface Farmer {
  id: number
  name: string
  phone: string
  email?: string
  location_lat?: number
  location_lon?: number
  preferred_lang: string
  created_at: string
  updated_at: string
}

export interface Farm {
  id: number
  farmer_id: number
  name: string
  crop_type: string
  sowing_date: string
  area_ha: number
  created_at: string
}

export class FarmerDatabase {
  private pool: Pool

  constructor() {
    this.pool = getPool()
  }

  async createFarmer(farmerData: {
    name: string
    phone: string
    email?: string
    location_lat?: number
    location_lon?: number
    preferred_lang?: string
  }): Promise<Farmer> {
    const query = `
      INSERT INTO farmers (name, phone, email, location_lat, location_lon, preferred_lang)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `
    
    const values = [
      farmerData.name,
      farmerData.phone,
      farmerData.email || null,
      farmerData.location_lat || null,
      farmerData.location_lon || null,
      farmerData.preferred_lang || 'en'
    ]

    const result = await this.pool.query(query, values)
    return result.rows[0]
  }

  async getFarmerByPhone(phone: string): Promise<Farmer | null> {
    const query = 'SELECT * FROM farmers WHERE phone = $1'
    const result = await this.pool.query(query, [phone])
    return result.rows[0] || null
  }

  async getFarmerById(id: number): Promise<Farmer | null> {
    const query = 'SELECT * FROM farmers WHERE id = $1'
    const result = await this.pool.query(query, [id])
    return result.rows[0] || null
  }

  async updateFarmer(id: number, updates: Partial<Farmer>): Promise<Farmer> {
    const setClause = Object.keys(updates)
      .map((key, index) => `${key} = $${index + 2}`)
      .join(', ')
    
    const query = `
      UPDATE farmers 
      SET ${setClause}, updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING *
    `
    
    const values = [id, ...Object.values(updates)]
    const result = await this.pool.query(query, values)
    return result.rows[0]
  }

  async getFarmerFarms(farmerId: number): Promise<Farm[]> {
    const query = 'SELECT * FROM farms WHERE farmer_id = $1 ORDER BY created_at DESC'
    const result = await this.pool.query(query, [farmerId])
    return result.rows
  }

  async createFarm(farmData: {
    farmer_id: number
    name: string
    crop_type: string
    sowing_date: string
    area_ha: number
  }): Promise<Farm> {
    const query = `
      INSERT INTO farms (farmer_id, name, crop_type, sowing_date, area_ha)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `
    
    const values = [
      farmData.farmer_id,
      farmData.name,
      farmData.crop_type,
      farmData.sowing_date,
      farmData.area_ha
    ]

    const result = await this.pool.query(query, values)
    return result.rows[0]
  }

  async updateFarm(id: number, updates: Partial<Farm>): Promise<Farm> {
    const setClause = Object.keys(updates)
      .map((key, index) => `${key} = $${index + 2}`)
      .join(', ')
    
    const query = `
      UPDATE farms 
      SET ${setClause}
      WHERE id = $1
      RETURNING *
    `
    
    const values = [id, ...Object.values(updates)]
    const result = await this.pool.query(query, values)
    return result.rows[0]
  }

  async deleteFarm(id: number): Promise<void> {
    const query = 'DELETE FROM farms WHERE id = $1'
    await this.pool.query(query, [id])
  }

  async getAllFarmers(): Promise<Farmer[]> {
    const query = 'SELECT * FROM farmers ORDER BY created_at DESC'
    const result = await this.pool.query(query)
    return result.rows
  }

  async initializeTables(): Promise<void> {
    const createFarmersTable = `
      CREATE TABLE IF NOT EXISTS farmers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(20) UNIQUE NOT NULL,
        email VARCHAR(255),
        location_lat DECIMAL(10, 8),
        location_lon DECIMAL(11, 8),
        preferred_lang VARCHAR(10) DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `

    const createFarmsTable = `
      CREATE TABLE IF NOT EXISTS farms (
        id SERIAL PRIMARY KEY,
        farmer_id INTEGER REFERENCES farmers(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        crop_type VARCHAR(100) NOT NULL,
        sowing_date DATE NOT NULL,
        area_ha DECIMAL(10, 4) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `

    await this.pool.query(createFarmersTable)
    await this.pool.query(createFarmsTable)
  }
}

export const farmerDb = new FarmerDatabase()