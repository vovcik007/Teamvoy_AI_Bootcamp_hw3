import { PrismaClient, UserRole, ContactRole, DealStage, ActivityType } from '@prisma/client';
import bcrypt from 'bcryptjs';
import 'dotenv/config'; // ✅ Завантажує змінні з файлу .env

const prisma = new PrismaClient();

async function main() {
  // ✅ 1. Читаємо пароль зі змінних середовища
  const agentPassword = process.env.AGENT_PASSWORD;
  
  // ✅ 2. Запобігаємо запуску, якщо пароль не налаштовано (захист від випадкового seed без .env)
  if (!agentPassword) {
    throw new Error('❌ AGENT_PASSWORD is not set in .env file! Please add it before running seed.');
  }

  // ✅ 3. Хешуємо пароль, отриманий з .env, а не літерал з коду
  const passwordHash = await bcrypt.hash(agentPassword, 10);

  // 4. Create User (Service User for the Agent)
  const user = await prisma.user.upsert({
    where: { email: 'agent@realty.com' },
    update: {},
    create: { 
      email: 'agent@realty.com', 
      passwordHash, 
      role: UserRole.AGENT 
    },
  });

  // 5. Create Company
  const company = await prisma.company.create({
    data: { name: 'Sunset Realty', domain: 'sunset-realty.com' },
  });

  // 6. Create Contacts
  const buyer = await prisma.contact.create({
    data: { 
      name: 'John Doe', 
      email: 'john@example.com', 
      phone: '+1234567890', 
      role: ContactRole.BUYER, 
      companyId: company.id 
    },
  });
  
  const seller = await prisma.contact.create({
    data: { 
      name: 'Jane Smith', 
      email: 'jane@example.com', 
      role: ContactRole.SELLER, 
      companyId: company.id 
    },
  });

  // 7. Create Deal
  const deal = await prisma.deal.create({
    data: { 
      title: '123 Ocean Drive, Miami', 
      stage: DealStage.VIEWING, 
      amount: 1250000, 
      companyId: company.id, 
      contactId: buyer.id 
    },
  });

  // 8. Create Activity
  await prisma.activity.create({
    data: { 
      type: ActivityType.SHOWING, 
      note: 'Scheduled weekend viewing', 
      dueAt: new Date(), 
      dealId: deal.id 
    },
  });

  console.log('✅ Seed data created successfully');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => await prisma.$disconnect());