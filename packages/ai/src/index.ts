import OpenAI from 'openai';

export interface GenerationRequest {
  systemPrompt?: string;
  userPrompt: string;
  temperature?: number;
}

export interface GenerationResponse {
  content: string;
  usage?: {
    promptTokens?: number;
    completionTokens?: number;
    totalTokens?: number;
  };
}

export interface TextGenerator {
  generateText: (request: GenerationRequest) => Promise<GenerationResponse>;
}

export function createOpenAITextGenerator(apiKey?: string): TextGenerator {
  const resolvedKey = apiKey ?? process.env.OPENAI_API_KEY;
  if (!resolvedKey) {
    return {
      async generateText({ userPrompt }: GenerationRequest): Promise<GenerationResponse> {
        const safe = (userPrompt || 'component').slice(0, 200);
        const fallback = `export default function GeneratedComponent() {
  return (
    <div className=\"rounded-xl border p-6 shadow-sm\">\n      <h2 className=\"mb-2 text-xl font-semibold\">Generated (local fallback)</h2>\n      <p className=\"text-sm text-neutral-600\">No OPENAI_API_KEY set. This is a placeholder for: <em>${safe}</em></p>\n    </div>\n  );
}`;
        return { content: fallback };
      },
    };
  }

  const client = new OpenAI({ apiKey: resolvedKey });
  return {
    async generateText({ systemPrompt, userPrompt, temperature = 0.2 }: GenerationRequest): Promise<GenerationResponse> {
      const response = await client.chat.completions.create({
        model: 'gpt-4o-mini',
        temperature,
        messages: [
          systemPrompt ? { role: 'system', content: systemPrompt } : null,
          { role: 'user', content: userPrompt },
        ].filter(Boolean) as any,
      });
      const choice = response.choices[0];
      return {
        content: choice.message?.content ?? '',
        usage: {
          promptTokens: response.usage?.prompt_tokens,
          completionTokens: response.usage?.completion_tokens,
          totalTokens: response.usage?.total_tokens,
        },
      };
    },
  };
}