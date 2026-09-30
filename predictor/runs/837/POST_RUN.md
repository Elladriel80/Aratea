**Run 837 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Sep 29, 2026?
Bin cible : `KXLOWTDEN-26SEP29-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.294, Brier=0.4989, P&L réel=$-65.62
- `learned_v2` (challenger) — p_yes=0.102, Brier=0.8065, P&L théorique=$-65.62
- `kalshi_mid_baseline` (baseline) — p_yes=0.375, Brier=0.3906, P&L théorique=$-65.62 ⭐

Verdict run 837 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/837/report.json
