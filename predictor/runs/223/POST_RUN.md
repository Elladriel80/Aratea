**Run 223 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 14, 2026?
Bin cible : `KXLOWTNYC-26JUN14-B68.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.173, Brier=0.0300, P&L réel=$+18.91
- `learned_v2` (challenger) — p_yes=0.034, Brier=0.0011, P&L théorique=$+18.91 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.0930, P&L théorique=$+18.91

Verdict run 223 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/223/report.json
