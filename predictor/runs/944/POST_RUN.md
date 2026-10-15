**Run 944 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 14, 2026?
Bin cible : `KXHIGHTDC-26OCT14-B83.5` · Outcome : NO · Low observée (bin gagnant) : 89-90°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.027, Brier=0.0007, P&L réel=$-60.03
- `learned_v2` (challenger) — p_yes=0.122, Brier=0.0149, P&L théorique=$-60.03
- `kalshi_mid_baseline` (baseline) — p_yes=0.025, Brier=0.0006, P&L théorique=$-60.03 ⭐

Verdict run 944 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/944/report.json
