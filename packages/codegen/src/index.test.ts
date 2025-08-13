import { describe, it, expect } from 'vitest';
import { generateReactComponentFromPrompt } from './index';

describe('generateReactComponentFromPrompt', () => {
  it('returns TSX string for a prompt (works with local fallback)', async () => {
    const code = await generateReactComponentFromPrompt({ prompt: 'A simple hello world component' });
    expect(code).toContain('function');
  });
});