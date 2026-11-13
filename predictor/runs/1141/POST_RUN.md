**Run 1141 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 11, 2026?
Bin cible : `KXLOWTNYC-26NOV11-B48.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.055, Brier=0.0030, P&L réel=$+134.47 ⭐
- `learned_v2` (challenger) — p_yes=0.147, Brier=0.0216, P&L théorique=$+134.47
- `kalshi_mid_baseline` (baseline) — p_yes=0.565, Brier=0.3192, P&L théorique=$+134.47

Verdict run 1141 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1141/report.json
