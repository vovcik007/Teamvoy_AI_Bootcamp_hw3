import express from 'express';
import cors from 'cors';
import routes from './routes.js';
import { errorHandler } from './errors.js';

const app = express();

app.use(cors());
app.use(express.json());

// Healthcheck для агента та Docker
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// API Routes
app.use('/', routes);

// Global Error Handler
app.use(errorHandler);

export default app;