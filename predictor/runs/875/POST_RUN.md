**Run 875 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Oct 5, 2026?
Bin cible : `KXLOWTLAX-26OCT05-B74.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.297, Brier=0.0883, P&L réel=$+51.33 ⭐
- `learned_v2` (challenger) — p_yes=0.644, Brier=0.4154, P&L théorique=$+51.33
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.1892, P&L théorique=$+51.33

Verdict run 875 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/875/report.json
