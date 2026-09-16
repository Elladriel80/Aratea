**Run 728 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Sep 15, 2026?
Bin cible : `KXHIGHTDC-26SEP15-B79.5` · Outcome : NO · Low observée (bin gagnant) : ≤79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.308, Brier=0.0950, P&L réel=$+95.88 ⭐
- `learned_v2` (challenger) — p_yes=0.460, Brier=0.2115, P&L théorique=$+95.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.635, Brier=0.4032, P&L théorique=$+95.88

Verdict run 728 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/728/report.json
