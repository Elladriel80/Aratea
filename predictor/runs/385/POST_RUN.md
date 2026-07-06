**Run 385 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 5, 2026?
Bin cible : `KXLOWTDC-26JUL05-B75.5` · Outcome : YES · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.500, Brier=0.2504, P&L réel=$+176.64 ⭐
- `learned_v2` (challenger) — p_yes=0.404, Brier=0.3548, P&L théorique=$+176.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.4761, P&L théorique=$+176.64

Verdict run 385 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/385/report.json
