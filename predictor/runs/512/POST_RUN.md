**Run 512 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 21, 2026?
Bin cible : `KXLOWTLAX-26JUL21-B68.5` · Outcome : NO · Low observée (bin gagnant) : ≥69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.200, Brier=0.0399, P&L réel=$+97.28
- `learned_v2` (challenger) — p_yes=0.184, Brier=0.0339, P&L théorique=$+97.28 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.640, Brier=0.4096, P&L théorique=$+97.28

Verdict run 512 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/512/report.json
