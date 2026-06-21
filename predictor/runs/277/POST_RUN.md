**Run 277 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 20, 2026?
Bin cible : `KXLOWTDC-26JUN20-B65.5` · Outcome : YES · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.185, Brier=0.6634, P&L réel=$-37.70
- `learned_v2` (challenger) — p_yes=0.107, Brier=0.7981, P&L théorique=$-37.70
- `kalshi_mid_baseline` (baseline) — p_yes=0.420, Brier=0.3364, P&L théorique=$-37.70 ⭐

Verdict run 277 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/277/report.json
