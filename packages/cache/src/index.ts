import Redis from 'ioredis';

let redis: Redis | undefined;

export function getRedis(): Redis | undefined {
  const url = process.env.REDIS_URL;
  if (!url) return undefined;
  if (!redis) {
    redis = new Redis(url, { lazyConnect: true, maxRetriesPerRequest: 2 });
  }
  return redis;
}

export interface RateLimitOptions {
  key: string;
  windowSeconds: number;
  max: number;
}

export async function rateLimit(options: RateLimitOptions): Promise<{ allowed: boolean; remaining: number; resetIn: number }> {
  const client = getRedis();
  if (!client) {
    return { allowed: true, remaining: options.max, resetIn: options.windowSeconds };
  }
  const now = Math.floor(Date.now() / 1000);
  const windowKey = `rl:${options.key}:${Math.floor(now / options.windowSeconds)}`;
  const count = await client.incr(windowKey);
  if (count === 1) {
    await client.expire(windowKey, options.windowSeconds);
  }
  const remaining = Math.max(0, options.max - count);
  return { allowed: count <= options.max, remaining, resetIn: options.windowSeconds - (now % options.windowSeconds) };
}