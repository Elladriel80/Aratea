**Run 842 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 1, 2026?
Bin cible : `KXLOWTSFO-26OCT01-B57.5` · Outcome : NO · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.514, Brier=0.2642, P&L réel=$-68.58
- `learned_v2` (challenger) — p_yes=0.801, Brier=0.6422, P&L théorique=$-68.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.0210, P&L théorique=$-68.58 ⭐

Verdict run 842 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/842/report.json
