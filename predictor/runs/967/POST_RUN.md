**Run 967 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 18, 2026?
Bin cible : `KXLOWTNYC-26OCT18-B39.5` · Outcome : NO · Low observée (bin gagnant) : 41-42°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.410, Brier=0.1679, P&L réel=$+130.98
- `learned_v2` (challenger) — p_yes=0.240, Brier=0.0577, P&L théorique=$+130.98 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.590, Brier=0.3481, P&L théorique=$+130.98

Verdict run 967 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/967/report.json
