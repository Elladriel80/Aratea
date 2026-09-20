**Run 750 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Sep 19, 2026?
Bin cible : `KXLOWTSFO-26SEP19-B59.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.532, Brier=0.2828, P&L réel=$-51.44
- `learned_v2` (challenger) — p_yes=0.837, Brier=0.6997, P&L théorique=$-51.44
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.1640, P&L théorique=$-51.44 ⭐

Verdict run 750 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/750/report.json
