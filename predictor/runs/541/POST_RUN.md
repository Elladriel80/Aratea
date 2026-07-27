**Run 541 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 25, 2026?
Bin cible : `KXLOWTNYC-26JUL25-B65.5` · Outcome : YES · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.297, Brier=0.4935, P&L réel=$-78.28
- `learned_v2` (challenger) — p_yes=0.112, Brier=0.7878, P&L théorique=$-78.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.495, Brier=0.2550, P&L théorique=$-78.28 ⭐

Verdict run 541 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/541/report.json
