import { z } from 'zod';
import { createOpenAITextGenerator } from '@acme/ai';

export const GenerationSchema = z.object({
  prompt: z.string().min(1),
  temperature: z.number().min(0).max(1).optional(),
});

const SYSTEM_PROMPT = `You are a senior front-end engineer. Generate a single React component in TSX named GeneratedComponent.
- Use only React and Tailwind classes. No external imports.
- No explanations, only the TSX code in a single block.
- The component should be self-contained and not depend on external state.
- Export default function GeneratedComponent(): JSX.Element { ... }`;

export async function generateReactComponentFromPrompt(input: z.infer<typeof GenerationSchema>): Promise<string> {
  const parsed = GenerationSchema.parse(input);
  const generator = createOpenAITextGenerator();
  const { content } = await generator.generateText({
    systemPrompt: SYSTEM_PROMPT,
    userPrompt: parsed.prompt,
    temperature: parsed.temperature ?? 0.2,
  });
  return content.trim();
}