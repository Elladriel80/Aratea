**Run 043 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on May 24, 2026?
Bin cible : `KXLOWTMIA-26MAY24-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.300, Brier=0.4901, P&L réel=$-20.43
- `learned_v2` (challenger) — p_yes=0.417, Brier=0.3395, P&L théorique=$-20.43
- `kalshi_mid_baseline` (baseline) — p_yes=0.525, Brier=0.2256, P&L théorique=$-20.43 ⭐

Verdict run 043 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/043/report.json
