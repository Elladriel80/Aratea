**Run 064 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on May 26, 2026?
Bin cible : `KXLOWTMIA-26MAY26-B78.5` · Outcome : NO · Low observée (bin gagnant) : 80-81°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.286, Brier=0.0816, P&L réel=$+17.10 ⭐
- `learned_v2` (challenger) — p_yes=0.390, Brier=0.1524, P&L théorique=$+17.10
- `kalshi_mid_baseline` (baseline) — p_yes=0.450, Brier=0.2025, P&L théorique=$+17.10

Verdict run 064 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/064/report.json
