**Run 1186 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Nov 16, 2026?
Bin cible : `KXHIGHTDC-26NOV16-B55.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.312, Brier=0.0974, P&L réel=$-135.30
- `learned_v2` (challenger) — p_yes=0.615, Brier=0.3786, P&L théorique=$-135.30
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.0225, P&L théorique=$-135.30 ⭐

Verdict run 1186 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1186/report.json
