**Run 1189 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 22, 2026?
Bin cible : `KXLOWTNYC-26NOV22-B48.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.356, Brier=0.1269, P&L réel=$-136.13
- `learned_v2` (challenger) — p_yes=0.704, Brier=0.4962, P&L théorique=$-136.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.055, Brier=0.0030, P&L théorique=$-136.13 ⭐

Verdict run 1189 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1189/report.json
