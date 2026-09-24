**Run 790 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Sep 23, 2026?
Bin cible : `KXHIGHTDC-26SEP23-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.260, Brier=0.5478, P&L réel=$-56.52
- `learned_v2` (challenger) — p_yes=0.509, Brier=0.2409, P&L théorique=$-56.52 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.3540, P&L théorique=$-56.52

Verdict run 790 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/790/report.json
