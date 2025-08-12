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

export async function createGeneration(params: { prompt: string; code: string; projectName?: string }) {
  const db = getPrisma();
  let projectId: string | undefined;
  if (params.projectName) {
    const project = await upsertProject(params.projectName, params.prompt);
    projectId = project.id;
  }
  return db.generation.create({
    data: {
      prompt: params.prompt,
      code: params.code,
      projectId,
    },
  });
}

export async function listGenerations(limit = 20) {
  const db = getPrisma();
  return db.generation.findMany({ orderBy: { createdAt: 'desc' }, take: limit });
}