**Run 1014 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 22, 2026?
Bin cible : `KXHIGHTDC-26OCT22-B67.5` · Outcome : NO · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.300, Brier=0.0898, P&L réel=$-29.55
- `learned_v2` (challenger) — p_yes=0.149, Brier=0.0221, P&L théorique=$-29.55
- `kalshi_mid_baseline` (baseline) — p_yes=0.115, Brier=0.0132, P&L théorique=$-29.55 ⭐

Verdict run 1014 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1014/report.json
