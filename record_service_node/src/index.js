
import express from 'express';
import { app_config } from './config.js';
import availabilityRoutes from './routes/availabilityRoutes.js';
import errorHandler from './middleware/errorHandler.js';
import cors from 'cors'
const app = express();
const port = app_config.port;


app.use(cors()); 
app.use(express.json());

app.use((req, res, next) => {
    console.log(`Incoming request: ${req.method} ${req.originalUrl}`);
    // console.log(`Incoming request: ${res}`);
    next();
});
// Use the availability routes
app.use('', availabilityRoutes);

// Error handling middleware
app.use(errorHandler);

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});