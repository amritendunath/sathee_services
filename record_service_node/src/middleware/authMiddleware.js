import jwt from 'jsonwebtoken';
import {app_config} from '../config.js';

const secretKey = app_config.jwtSecret;

const verifyToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        console.log('No token provided');
        return res.status(401).json({ message: 'No token provided' });
    }

    jwt.verify(token, secretKey, (err, decoded) => {
        if (err) {
            console.error('Failed to authenticate token:', err);
            return res.status(403).json({ message: 'Failed to authenticate token' });
        }
        req.user_id  = decoded.user_ehr_id;
        console.log('User ID extracted from token:', req.user_id);
        next();
    });
};

export default verifyToken