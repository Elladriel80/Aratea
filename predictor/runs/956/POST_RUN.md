**Run 956 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 16, 2026?
Bin cible : `KXLOWTMIA-26OCT16-B75.5` · Outcome : YES · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.299, Brier=0.4918, P&L réel=$+1716.73 ⭐
- `learned_v2` (challenger) — p_yes=0.094, Brier=0.8211, P&L théorique=$+1716.73
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.9312, P&L théorique=$+1716.73

Verdict run 956 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/956/report.json
