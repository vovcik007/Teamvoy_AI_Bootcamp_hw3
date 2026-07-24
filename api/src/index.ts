import app from './app.js';
import { env } from './env.js';
import { prisma } from './prisma.js';

async function bootstrap() {
  try {
    await prisma.$connect();
    console.log('✅ Database connected');
    
    app.listen(env.PORT, () => {
      console.log(`🚀 CRM API is running on http://localhost:${env.PORT}`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

bootstrap();