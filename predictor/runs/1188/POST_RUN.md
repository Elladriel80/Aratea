**Run 1188 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 22, 2026?
Bin cible : `KXLOWTNYC-26NOV22-B52.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.082, Brier=0.0068, P&L réel=$+141.27 ⭐
- `learned_v2` (challenger) — p_yes=0.179, Brier=0.0322, P&L théorique=$+141.27
- `kalshi_mid_baseline` (baseline) — p_yes=0.510, Brier=0.2601, P&L théorique=$+141.27

Verdict run 1188 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1188/report.json
