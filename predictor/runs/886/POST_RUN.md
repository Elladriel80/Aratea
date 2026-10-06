**Run 886 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 5, 2026?
Bin cible : `KXHIGHTDC-26OCT05-B73.5` · Outcome : YES · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.303, Brier=0.4857, P&L réel=$-66.42
- `learned_v2` (challenger) — p_yes=0.551, Brier=0.2015, P&L théorique=$-66.42 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.460, Brier=0.2916, P&L théorique=$-66.42

Verdict run 886 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/886/report.json
