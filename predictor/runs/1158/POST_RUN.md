**Run 1158 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 13, 2026?
Bin cible : `KXLOWTSFO-26NOV13-B51.5` · Outcome : NO · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.148, Brier=0.0218, P&L réel=$-96.64
- `learned_v2` (challenger) — p_yes=0.216, Brier=0.0465, P&L théorique=$-96.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.055, Brier=0.0030, P&L théorique=$-96.64 ⭐

Verdict run 1158 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1158/report.json
