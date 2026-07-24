import express from 'express';
import cors from 'cors';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import routes from './routes.js';
import { errorHandler } from './errors.js';
import { typeDefs } from './graphql/schema.js';
import { resolvers } from './graphql/resolvers.js';
import { buildContext } from './graphql/context.js';

const app = express();

app.use(cors());
app.use(express.json());

// Healthcheck
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// REST routes (для агента)
app.use('/', routes);

// ✅ GraphQL endpoint (для фронтенду/клієнтів)
async function startApollo() {
  const server = new ApolloServer({ typeDefs, resolvers });
  await server.start();
  
  app.use(
    '/graphql',
    cors<cors.CorsRequest>(),
    express.json(),
    expressMiddleware(server, { context: buildContext })
  );
}

// Global Error Handler (для REST)
app.use(errorHandler);

export default app;
export { startApollo };