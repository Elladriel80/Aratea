**Run 969 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 18, 2026?
Bin cible : `KXLOWTNYC-26OCT18-B41.5` · Outcome : YES · Low observée (bin gagnant) : 41-42°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.191, Brier=0.6542, P&L réel=$-90.75
- `learned_v2` (challenger) — p_yes=0.050, Brier=0.9033, P&L théorique=$-90.75
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.5625, P&L théorique=$-90.75 ⭐

Verdict run 969 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/969/report.json
