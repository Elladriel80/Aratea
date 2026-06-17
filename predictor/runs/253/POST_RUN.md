**Run 253 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 16, 2026?
Bin cible : `KXLOWTDEN-26JUN16-B50.5` · Outcome : NO · Low observée (bin gagnant) : ≤50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.103, Brier=0.0106, P&L réel=$+1.82 ⭐
- `learned_v2` (challenger) — p_yes=0.159, Brier=0.0253, P&L théorique=$+1.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.0272, P&L théorique=$+1.82

Verdict run 253 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/253/report.json
