**Run 824 — résolu YES · Multi-model A/B**

Event : Highest temperature in Seattle on Sep 27, 2026?
Bin cible : `KXHIGHTSEA-26SEP27-B65.5` · Outcome : YES · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.312, Brier=0.4734, P&L réel=$-27.65
- `learned_v2` (challenger) — p_yes=0.516, Brier=0.2345, P&L théorique=$-27.65
- `kalshi_mid_baseline` (baseline) — p_yes=0.605, Brier=0.1560, P&L théorique=$-27.65 ⭐

Verdict run 824 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/824/report.json
