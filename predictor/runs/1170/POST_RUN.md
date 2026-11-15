**Run 1170 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Nov 13, 2026?
Bin cible : `KXHIGHTDC-26NOV13-B53.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.069, Brier=0.0048, P&L réel=$+18.40 ⭐
- `learned_v2` (challenger) — p_yes=0.073, Brier=0.0054, P&L théorique=$+18.40
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.0256, P&L théorique=$+18.40

Verdict run 1170 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1170/report.json
