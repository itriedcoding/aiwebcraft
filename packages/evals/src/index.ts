export interface EvaluationMetric {
  id: string;
  label: string;
  score: (input: string) => Promise<number> | number;
}

export class Evaluator {
  private metrics: EvaluationMetric[] = [];

  addMetric(metric: EvaluationMetric): this {
    this.metrics.push(metric);
    return this;
  }

  async runAll(input: string): Promise<Record<string, number>> {
    const results: Record<string, number> = {};
    for (const metric of this.metrics) {
      const value = await metric.score(input);
      results[metric.id] = Math.max(0, Math.min(1, value));
    }
    return results;
  }
}