**Run 928 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Oct 11, 2026?
Bin cible : `KXLOWTPHX-26OCT11-B70.5` · Outcome : NO · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.166, Brier=0.0274, P&L réel=$+16.16 ⭐
- `learned_v2` (challenger) — p_yes=0.240, Brier=0.0575, P&L théorique=$+16.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.265, Brier=0.0702, P&L théorique=$+16.16

Verdict run 928 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/928/report.json
