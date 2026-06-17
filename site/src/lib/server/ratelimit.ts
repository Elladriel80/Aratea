/**
 * Limiteur de débit « fenêtre fixe » en mémoire. Anti-abus best-effort.
 *
 * Limite : sur Vercel (serverless), la mémoire est par-instance et éphémère, ce
 * n'est donc pas une garantie dure mais un frein contre les boucles bot
 * basiques. La défense de fond reste : le nonce à usage unique, la session
 * GitHub vérifiée, et la ratification humaine avant tout merge. Server-only.
 */

type Bucket = { count: number; resetAt: number };

const buckets = new Map<string, Bucket>();

export type RateResult = { ok: boolean; remaining: number; resetAt: number };

/**
 * Incrémente le compteur de `key` et indique si la requête passe sous la limite.
 * `now` est injectable pour les tests.
 */
export function checkRateLimit(
  key: string,
  limit: number,
  windowMs: number,
  now: number = Date.now(),
): RateResult {
  const b = buckets.get(key);
  if (!b || b.resetAt <= now) {
    const resetAt = now + windowMs;
    buckets.set(key, { count: 1, resetAt });
    return { ok: true, remaining: limit - 1, resetAt };
  }
  if (b.count >= limit) {
    return { ok: false, remaining: 0, resetAt: b.resetAt };
  }
  b.count += 1;
  return { ok: true, remaining: limit - b.count, resetAt: b.resetAt };
}

/** Vide tous les compteurs (tests). */
export function resetRateLimits(): void {
  buckets.clear();
}
