**Run 472 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 16, 2026?
Bin cible : `KXLOWTNYC-26JUL16-B74.5` · Outcome : YES · Low observée (bin gagnant) : 74-75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.139, Brier=0.7417, P&L réel=$-69.08
- `learned_v2` (challenger) — p_yes=0.026, Brier=0.9483, P&L théorique=$-69.08
- `kalshi_mid_baseline` (baseline) — p_yes=0.215, Brier=0.6162, P&L théorique=$-69.08 ⭐

Verdict run 472 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/472/report.json
