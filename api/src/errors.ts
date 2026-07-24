import { Request, Response, NextFunction } from 'express';

export class AppError extends Error {
  public statusCode: number;
  public code: string;

  constructor(message: string, statusCode: number, code: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ error: err.code, detail: err.message });
  }
  
  if (err.name === 'ZodError') {
    return res.status(400).json({ error: 'validation_error', detail: err.errors });
  }

  console.error('Unhandled error:', err);
  return res.status(500).json({ error: 'internal_server_error', detail: 'An unexpected error occurred' });
};