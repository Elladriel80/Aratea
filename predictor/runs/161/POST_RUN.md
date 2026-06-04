**Run 161 — résolu YES · Multi-model A/B**

Event : Highest temperature in Phoenix on Jun 3, 2026?
Bin cible : `KXHIGHTPHX-26JUN03-B107.5` · Outcome : YES · Low observée (bin gagnant) : 107-108°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.161, Brier=0.7041, P&L réel=$-7.58
- `learned_v2` (challenger) — p_yes=0.130, Brier=0.7563, P&L théorique=$-7.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.495, Brier=0.2550, P&L théorique=$-7.58 ⭐

Verdict run 161 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/161/report.json
