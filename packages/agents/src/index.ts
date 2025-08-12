import { z } from 'zod';

export type AgentStepContext = Record<string, unknown>;

export interface AgentStep<I, O> {
  name: string;
  run: (input: I, context: AgentStepContext) => Promise<O>;
}

export class AgentWorkflow<I, O> {
  private steps: AgentStep<any, any>[] = [];

  addStep<TIn, TOut>(step: AgentStep<TIn, TOut>): this {
    this.steps.push(step as AgentStep<any, any>);
    return this;
  }

  async execute(initialInput: I, context: AgentStepContext = {}): Promise<O> {
    let current: unknown = initialInput;
    for (const step of this.steps) {
      current = await step.run(current as never, context);
    }
    return current as O;
  }
}

export const JsonSchema = z.record(z.any());