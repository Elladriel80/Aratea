**Run 593 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Aug 1, 2026?
Bin cible : `KXLOWTLAX-26AUG01-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.372, Brier=0.1388, P&L réel=$+60.90
- `learned_v2` (challenger) — p_yes=0.234, Brier=0.0550, P&L théorique=$+60.90 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.1892, P&L théorique=$+60.90

Verdict run 593 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/593/report.json
