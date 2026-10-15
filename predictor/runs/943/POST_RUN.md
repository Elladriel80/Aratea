**Run 943 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 14, 2026?
Bin cible : `KXHIGHTDC-26OCT14-B85.5` · Outcome : NO · Low observée (bin gagnant) : 89-90°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.120, Brier=0.0145, P&L réel=$-77.28
- `learned_v2` (challenger) — p_yes=0.237, Brier=0.0564, P&L théorique=$-77.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.065, Brier=0.0042, P&L théorique=$-77.28 ⭐

Verdict run 943 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/943/report.json
