**Run 950 — résolu NO · Multi-model A/B**

Event : Highest temperature in Phoenix on Oct 14, 2026?
Bin cible : `KXHIGHTPHX-26OCT14-B79.5` · Outcome : NO · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.416, Brier=0.1734, P&L réel=$+28.98 ⭐
- `learned_v2` (challenger) — p_yes=0.783, Brier=0.6128, P&L théorique=$+28.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.475, Brier=0.2256, P&L théorique=$+28.98

Verdict run 950 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/950/report.json
