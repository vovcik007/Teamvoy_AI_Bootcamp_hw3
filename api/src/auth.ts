import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { env } from './env.js';
import { AppError } from './errors.js';

export const verifyPassword = async (password: string, hash: string) => bcrypt.compare(password, hash);
export const signToken = (userId: string) => jwt.sign({ sub: userId }, env.JWT_SECRET, { expiresIn: '15m' });

export interface AuthRequest extends Request {
  userId?: string;
}

export const requireAuth = (req: AuthRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return next(new AppError('Missing authorization header', 401, 'unauthorized'));
  }

  try {
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, env.JWT_SECRET) as { sub: string };
    req.userId = decoded.sub;
    next();
  } catch (err) {
    return next(new AppError('Invalid or expired token', 401, 'unauthorized'));
  }
};