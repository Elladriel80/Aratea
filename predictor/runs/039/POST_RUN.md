**Run 039 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on May 24, 2026?
Bin cible : `KXLOWTDC-26MAY24-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.200, Brier=0.6393, P&L réel=$-20.30
- `learned_v2` (challenger) — p_yes=0.126, Brier=0.7646, P&L théorique=$-20.30
- `kalshi_mid_baseline` (baseline) — p_yes=0.420, Brier=0.3364, P&L théorique=$-20.30 ⭐

Verdict run 039 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/039/report.json
