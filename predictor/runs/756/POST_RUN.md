**Run 756 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Sep 19, 2026?
Bin cible : `KXLOWTDEN-26SEP19-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.262, Brier=0.5443, P&L réel=$-51.20
- `learned_v2` (challenger) — p_yes=0.386, Brier=0.3765, P&L théorique=$-51.20 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.360, Brier=0.4096, P&L théorique=$-51.20

Verdict run 756 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/756/report.json
