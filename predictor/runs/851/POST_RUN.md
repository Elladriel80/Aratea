**Run 851 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Oct 1, 2026?
Bin cible : `KXHIGHTSEA-26OCT01-B63.5` · Outcome : NO · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.109, Brier=0.0119, P&L réel=$-66.05
- `learned_v2` (challenger) — p_yes=0.136, Brier=0.0184, P&L théorique=$-66.05
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-66.05 ⭐

Verdict run 851 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/851/report.json
