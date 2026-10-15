**Run 946 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Oct 14, 2026?
Bin cible : `KXHIGHTBOS-26OCT14-B75.5` · Outcome : NO · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.286, Brier=0.0816, P&L réel=$+44.16 ⭐
- `learned_v2` (challenger) — p_yes=0.550, Brier=0.3027, P&L théorique=$+44.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.365, Brier=0.1332, P&L théorique=$+44.16

Verdict run 946 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/946/report.json
