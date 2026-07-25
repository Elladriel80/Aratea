**Run 536 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 24, 2026?
Bin cible : `KXLOWTNYC-26JUL24-B64.5` · Outcome : YES · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.264, Brier=0.5415, P&L réel=$-56.52
- `learned_v2` (challenger) — p_yes=0.077, Brier=0.8519, P&L théorique=$-56.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.365, Brier=0.4032, P&L théorique=$-56.52 ⭐

Verdict run 536 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/536/report.json
