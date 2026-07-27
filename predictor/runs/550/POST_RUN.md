**Run 550 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 25, 2026?
Bin cible : `KXLOWTCHI-26JUL25-B64.5` · Outcome : YES · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.572, Brier=0.1829, P&L réel=$+112.10
- `learned_v2` (challenger) — p_yes=0.912, Brier=0.0077, P&L théorique=$+112.10 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.410, Brier=0.3481, P&L théorique=$+112.10

Verdict run 550 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/550/report.json
