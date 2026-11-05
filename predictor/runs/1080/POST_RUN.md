**Run 1080 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 2, 2026?
Bin cible : `KXLOWTNYC-26NOV02-B47.5` · Outcome : NO · Low observée (bin gagnant) : 43-44°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.190, Brier=0.0361, P&L réel=$+118.67 ⭐
- `learned_v2` (challenger) — p_yes=0.311, Brier=0.0965, P&L théorique=$+118.67
- `kalshi_mid_baseline` (baseline) — p_yes=0.505, Brier=0.2550, P&L théorique=$+118.67

Verdict run 1080 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1080/report.json
