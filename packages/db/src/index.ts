import { PrismaClient } from '@prisma/client';

let prisma: PrismaClient | undefined;

export function getPrisma(): PrismaClient {
  if (!prisma) {
    prisma = new PrismaClient();
  }
  return prisma;
}

export async function upsertProject(name: string, prompt?: string) {
  const db = getPrisma();
  return db.project.upsert({
    where: { name },
    update: { prompt },
    create: { name, prompt },
  });
}