import { GraphQLError } from 'graphql';
import { prisma } from '../prisma.js';
import { GraphQLContext } from './context.js';

// ✅ Helper: перевірка авторизації
function requireAuth(context: GraphQLContext) {
  if (!context.userId) {
    throw new GraphQLError('Unauthorized', {
      extensions: { code: 'UNAUTHENTICATED' },
    });
  }
}

export const resolvers = {
  // === QUERIES (читання) ===
  Query: {
    companies: async (_: unknown, args: { search?: string }) => {
      const where = args.search 
        ? { name: { contains: args.search, mode: 'insensitive' as const } }
        : {};
      return prisma.company.findMany({ where, orderBy: { createdAt: 'desc' } });
    },
    
    company: async (_: unknown, args: { id: string }) => 
      prisma.company.findUnique({ where: { id: args.id } }),
    
    contacts: async (_: unknown, args: { companyId?: string; role?: string }) => {
      const where: any = {};
      if (args.companyId) where.companyId = args.companyId;
      if (args.role) where.role = args.role;
      return prisma.contact.findMany({ where, orderBy: { createdAt: 'desc' } });
    },
    
    deals: async (_: unknown, args: { companyId?: string; contactId?: string; stage?: string }) => {
      const where: any = {};
      if (args.companyId) where.companyId = args.companyId;
      if (args.contactId) where.contactId = args.contactId;
      if (args.stage) where.stage = args.stage;
      return prisma.deal.findMany({ where, orderBy: { createdAt: 'desc' } });
    },
    
    activities: async (_: unknown, args: { dealId: string }) => 
      prisma.activity.findMany({ where: { dealId: args.dealId }, orderBy: { dueAt: 'asc' } }),
  },

  // === MUTATIONS (запис) — усі під auth ===
  Mutation: {
    createCompany: async (_: unknown, args: { name: string; domain?: string }, context: GraphQLContext) => {
      requireAuth(context);
      return prisma.company.create({ data: { name: args.name, domain: args.domain } });
    },
    
    createContact: async (_: unknown, args: any, context: GraphQLContext) => {
      requireAuth(context);
      return prisma.contact.create({
        data: {
          name: args.name,
          email: args.email,
          phone: args.phone,
          role: args.role || 'BUYER',
          companyId: args.companyId,
        },
      });
    },
    
    createDeal: async (_: unknown, args: any, context: GraphQLContext) => {
      requireAuth(context);
      return prisma.deal.create({
        data: {
          title: args.title,
          amount: args.amount,
          stage: args.stage || 'LEAD',
          companyId: args.companyId,
          contactId: args.contactId,
        },
      });
    },
    
    createActivity: async (_: unknown, args: any, context: GraphQLContext) => {
      requireAuth(context);
      return prisma.activity.create({
        data: {
          type: args.type,
          note: args.note,
          dueAt: args.dueAt ? new Date(args.dueAt) : undefined,
          dealId: args.dealId,
        },
      });
    },
  },

  // === NESTED RESOLVERS (головна фіча GraphQL!) ===
  Company: {
    contacts: (parent: any) => 
      prisma.contact.findMany({ where: { companyId: parent.id } }),
    deals: (parent: any) => 
      prisma.deal.findMany({ where: { companyId: parent.id } }),
  },
  
  Contact: {
    company: (parent: any) => 
      prisma.company.findUnique({ where: { id: parent.companyId } }),
    deals: (parent: any) => 
      prisma.deal.findMany({ where: { contactId: parent.id } }),
  },
  
  Deal: {
    company: (parent: any) => 
      prisma.company.findUnique({ where: { id: parent.companyId } }),
    contact: (parent: any) => 
      parent.contactId ? prisma.contact.findUnique({ where: { id: parent.contactId } }) : null,
    activities: (parent: any) => 
      prisma.activity.findMany({ where: { dealId: parent.id } }),
  },
  
  Activity: {
    deal: (parent: any) => 
      prisma.deal.findUnique({ where: { id: parent.dealId } }),
  },
};