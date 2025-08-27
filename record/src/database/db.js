
import pg from 'pg';
import {db_config} from '../config.js';
const { Pool } = pg;
const pool = new Pool(db_config);

// Export a query function that uses the pool
const query = (text, params) => pool.query(text, params);

// Export the pool and query function
export {
    pool,
    query
};