**Run 1164 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Nov 13, 2026?
Bin cible : `KXLOWTSEA-26NOV13-B47.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.039, Brier=0.0015, P&L réel=$+25.62 ⭐
- `learned_v2` (challenger) — p_yes=0.059, Brier=0.0035, P&L théorique=$+25.62
- `kalshi_mid_baseline` (baseline) — p_yes=0.210, Brier=0.0441, P&L théorique=$+25.62

Verdict run 1164 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1164/report.json
