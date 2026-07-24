import { z } from 'zod';

export const createCompanySchema = z.object({
  name: z.string().min(1),
  domain: z.string().optional().or(z.literal('')),
});

export const createContactSchema = z.object({
  name: z.string().min(1),
  email: z.string().email().optional().or(z.literal('')),
  phone: z.string().optional().or(z.literal('')),
  role: z.enum(['BUYER', 'SELLER', 'BOTH']).optional(),
  company_id: z.string().uuid(), // ✅ Агент шле саме це
});

export const createDealSchema = z.object({
  title: z.string().min(1),
  stage: z.enum(['LEAD', 'VIEWING', 'OFFER', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST']).optional(),
  amount: z.number().positive().optional(),
  company_id: z.string().uuid(), // ✅ Агент шле саме це
  contact_id: z.string().uuid().optional(), // ✅ Агент шле саме це
});

export const createActivitySchema = z.object({
  type: z.enum(['CALL', 'EMAIL', 'SHOWING', 'OFFER', 'MEETING', 'OTHER']),
  note: z.string().optional().or(z.literal('')),
  dueAt: z.string().datetime().optional().or(z.literal('')),
  deal_id: z.string().uuid(), // ✅ Агент шле саме це
});

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});