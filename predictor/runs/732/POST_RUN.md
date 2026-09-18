**Run 732 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 17, 2026?
Bin cible : `KXLOWTBOS-26SEP17-B65.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.303, Brier=0.0919, P&L réel=$+48.60 ⭐
- `learned_v2` (challenger) — p_yes=0.511, Brier=0.2614, P&L théorique=$+48.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.450, Brier=0.2025, P&L théorique=$+48.60

Verdict run 732 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/732/report.json
