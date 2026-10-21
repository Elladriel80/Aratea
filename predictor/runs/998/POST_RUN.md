**Run 998 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 20, 2026?
Bin cible : `KXHIGHTDC-26OCT20-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.342, Brier=0.4328, P&L réel=$-2.97
- `learned_v2` (challenger) — p_yes=0.143, Brier=0.7338, P&L théorique=$-2.97
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.3540, P&L théorique=$-2.97 ⭐

Verdict run 998 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/998/report.json
