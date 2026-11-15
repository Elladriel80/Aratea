**Run 1163 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Nov 13, 2026?
Bin cible : `KXLOWTSEA-26NOV13-B51.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.009, Brier=0.0001, P&L réel=$+30.48 ⭐
- `learned_v2` (challenger) — p_yes=0.007, Brier=0.0001, P&L théorique=$+30.48
- `kalshi_mid_baseline` (baseline) — p_yes=0.240, Brier=0.0576, P&L théorique=$+30.48

Verdict run 1163 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1163/report.json
