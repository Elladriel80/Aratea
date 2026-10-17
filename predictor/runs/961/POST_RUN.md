**Run 961 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Oct 16, 2026?
Bin cible : `KXLOWTSEA-26OCT16-B48.5` · Outcome : NO · Low observée (bin gagnant) : 46-47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.176, Brier=0.0309, P&L réel=$+34.08 ⭐
- `learned_v2` (challenger) — p_yes=0.196, Brier=0.0385, P&L théorique=$+34.08
- `kalshi_mid_baseline` (baseline) — p_yes=0.355, Brier=0.1260, P&L théorique=$+34.08

Verdict run 961 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/961/report.json
