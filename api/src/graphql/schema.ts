import { gql } from 'graphql-tag';

export const typeDefs = gql`
  # Enums (мапимо на Prisma enums)
  enum UserRole { ADMIN AGENT }
  enum ContactRole { BUYER SELLER BOTH }
  enum DealStage { LEAD VIEWING OFFER NEGOTIATION CLOSED_WON CLOSED_LOST }
  enum ActivityType { CALL EMAIL SHOWING OFFER MEETING OTHER }

  # Types
  type User {
    id: ID!
    email: String!
    role: UserRole!
    createdAt: String!
  }

  type Company {
    id: ID!
    name: String!
    domain: String
    contacts: [Contact!]!      # ✅ Nested resolver
    deals: [Deal!]!            # ✅ Nested resolver
    createdAt: String!
  }

  type Contact {
    id: ID!
    name: String!
    email: String
    phone: String
    role: ContactRole!
    company: Company!          # ✅ Nested resolver
    deals: [Deal!]!
    createdAt: String!
  }

  type Deal {
    id: ID!
    title: String!
    stage: DealStage!
    amount: Float
    company: Company!          # ✅ Nested resolver
    contact: Contact
    activities: [Activity!]!   # ✅ Nested resolver
    createdAt: String!
  }

  type Activity {
    id: ID!
    type: ActivityType!
    note: String
    dueAt: String
    deal: Deal!                # ✅ Nested resolver
    createdAt: String!
  }

  # Queries
  type Query {
    companies(search: String): [Company!]!
    company(id: ID!): Company
    contacts(companyId: ID, role: ContactRole): [Contact!]!
    contact(id: ID!): Contact
    deals(companyId: ID, contactId: ID, stage: DealStage): [Deal!]!
    deal(id: ID!): Deal
    activities(dealId: ID!): [Activity!]!
  }

  # Mutations (write-операції)
  type Mutation {
    createCompany(name: String!, domain: String): Company!
    createContact(name: String!, companyId: ID!, email: String, phone: String, role: ContactRole): Contact!
    createDeal(title: String!, companyId: ID!, contactId: ID, amount: Float, stage: DealStage): Deal!
    createActivity(type: ActivityType!, dealId: ID!, note: String, dueAt: String): Activity!
  }
`;