**Run 509 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 21, 2026?
Bin cible : `KXLOWTNYC-26JUL21-B68.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.058, Brier=0.0033, P&L réel=$+21.66 ⭐
- `learned_v2` (challenger) — p_yes=0.076, Brier=0.0058, P&L théorique=$+21.66
- `kalshi_mid_baseline` (baseline) — p_yes=0.285, Brier=0.0812, P&L théorique=$+21.66

Verdict run 509 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/509/report.json
