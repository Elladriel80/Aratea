**Run 776 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Sep 21, 2026?
Bin cible : `KXLOWTSEA-26SEP21-B52.5` · Outcome : YES · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.344, Brier=0.4299, P&L réel=$+234.09
- `learned_v2` (challenger) — p_yes=0.428, Brier=0.3277, P&L théorique=$+234.09 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.190, Brier=0.6561, P&L théorique=$+234.09

Verdict run 776 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/776/report.json
