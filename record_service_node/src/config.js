import dotenv from 'dotenv'
dotenv.config()

const db_config = {
    'host': process.env.DBHOST,
    'port': process.env.DBPORT,
    'database': process.env.DBNAME,
    'user': process.env.DBUSER,
    // 'password': process.env.DBPASS,
    // 'ssl': {
    //     rejectUnauthorized: false // Only for development.  Set to true in production
    // }
};

const redis_config = {
    'host': process.env.REDHOST,
    'port': process.env.REDPORT,
    'db': process.env.REDDB,
    'decode_responses': process.env.REDDECRES
}
const app_config = {
    port: process.env.PORT,
    jwtSecret: process.env.JWT_SECRET_KEY
};


export {
    db_config,
    redis_config,
    app_config
}