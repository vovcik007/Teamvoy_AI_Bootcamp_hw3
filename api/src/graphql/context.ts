import { Request } from 'express';
import jwt from 'jsonwebtoken';
import { env } from '../env.js';

export interface GraphQLContext {
  userId?: string;
}

// ✅ Додаємо async, щоб повертати Promise
export async function buildContext({ req }: { req: Request }): Promise<GraphQLContext> {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return {}; // Неавторизований
  }

  try {
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, env.JWT_SECRET) as { sub: string };
    return { userId: decoded.sub };
  } catch (err) {
    return {}; // Невалідний токен
  }
}