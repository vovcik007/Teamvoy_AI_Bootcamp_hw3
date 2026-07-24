import { Router, Request, Response, NextFunction } from 'express';
import { Prisma, ContactRole, DealStage } from '@prisma/client'; // ✅ Імпортуємо типи Prisma
import { prisma } from './prisma.js';
import { requireAuth, signToken, verifyPassword, AuthRequest } from './auth.js';
import { AppError } from './errors.js';
import { 
  loginSchema, createCompanySchema, createContactSchema, 
  createDealSchema, createActivitySchema 
} from './validation.js';

const router = Router();

// --- AUTH ---
router.post('/auth/login', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = loginSchema.parse(req.body);
    const user = await prisma.user.findUnique({ where: { email } });
    
    if (!user || !(await verifyPassword(password, user.passwordHash))) {
      throw new AppError('Invalid credentials', 401, 'unauthorized');
    }
    
    res.json({ access_token: signToken(user.id) });
  } catch (err) { next(err); }
});

// --- COMPANIES ---
router.get('/companies', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { search } = req.query;
    
    // ✅ Виправлення помилки: використовуємо Prisma.CompanyWhereInput
    // TypeScript тепер точно знає, що mode - це 'insensitive', а не просто string
    const where: Prisma.CompanyWhereInput = search 
      ? { name: { contains: String(search), mode: 'insensitive' } } 
      : {};
      
    const companies = await prisma.company.findMany({ where, orderBy: { createdAt: 'desc' } });
    res.json(companies);
  } catch (err) { next(err); }
});

router.post('/companies', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const data = createCompanySchema.parse(req.body);
    const company = await prisma.company.create({ data });
    res.status(201).json(company);
  } catch (err) { next(err); }
});

// --- CONTACTS ---
router.get('/contacts', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { companyId, role } = req.query;
    
    // ✅ Прибираємо 'any', використовуємо строгий тип
    const where: Prisma.ContactWhereInput = {};
    if (companyId) where.companyId = String(companyId);
    if (role) where.role = String(role) as ContactRole; // Кастуємо до енуму
    
    const contacts = await prisma.contact.findMany({ where, orderBy: { createdAt: 'desc' } });
    res.json(contacts);
  } catch (err) { next(err); }
});

router.post('/contacts', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const data = createContactSchema.parse(req.body);
    const contact = await prisma.contact.create({
      data: {
        name: data.name,
        email: data.email || undefined,
        phone: data.phone || undefined,
        role: data.role || 'BUYER',
        companyId: data.company_id, // ✅ Мапінг snake_case -> camelCase для Prisma
      }
    });
    res.status(201).json(contact);
  } catch (err) { next(err); }
});

// --- DEALS ---
router.get('/deals', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { companyId, contactId, stage } = req.query;
    
    // ✅ Прибираємо 'any', використовуємо строгий тип
    const where: Prisma.DealWhereInput = {};
    if (companyId) where.companyId = String(companyId);
    if (contactId) where.contactId = String(contactId);
    if (stage) where.stage = String(stage) as DealStage; // Кастуємо до енуму
    
    const deals = await prisma.deal.findMany({ where, orderBy: { createdAt: 'desc' } });
    res.json(deals);
  } catch (err) { next(err); }
});
router.post('/deals', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const data = createDealSchema.parse(req.body);
    const deal = await prisma.deal.create({
      data: {
        title: data.title,
        stage: data.stage || 'LEAD',
        amount: data.amount,
        companyId: data.company_id, // ✅ Мапінг
        contactId: data.contact_id || undefined, // ✅ Мапінг
      }
    });
    res.status(201).json(deal);
  } catch (err) { next(err); }
});

// --- ACTIVITIES ---
router.get('/activities', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { dealId } = req.query;
    const where = dealId ? { dealId: String(dealId) } : {};
    const activities = await prisma.activity.findMany({ where, orderBy: { dueAt: 'asc' } });
    res.json(activities);
  } catch (err) { next(err); }
});

router.post('/activities', requireAuth, async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const data = createActivitySchema.parse(req.body);
    const activity = await prisma.activity.create({
      data: {
        type: data.type,
        note: data.note || undefined,
        dueAt: data.dueAt ? new Date(data.dueAt) : undefined,
        dealId: data.deal_id, // ✅ Мапінг
      }
    });
    res.status(201).json(activity);
  } catch (err) { next(err); }
});

export default router;