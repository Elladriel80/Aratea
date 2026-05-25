**Run 049 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on May 24, 2026?
Bin cible : `KXLOWTDEN-26MAY24-B48.5` · Outcome : NO · Low observée (bin gagnant) : ≥51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.107, Brier=0.0114, P&L réel=$+6.89 ⭐
- `learned_v2` (challenger) — p_yes=0.169, Brier=0.0286, P&L théorique=$+6.89
- `kalshi_mid_baseline` (baseline) — p_yes=0.255, Brier=0.0650, P&L théorique=$+6.89

Verdict run 049 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/049/report.json
