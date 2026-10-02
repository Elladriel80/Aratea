**Run 855 — résolu YES · Multi-model A/B**

Event : Highest temperature in Atlanta on Oct 1, 2026?
Bin cible : `KXHIGHTATL-26OCT01-B85.5` · Outcome : YES · Low observée (bin gagnant) : 85-86°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.107, Brier=0.7979, P&L réel=$-68.11
- `learned_v2` (challenger) — p_yes=0.040, Brier=0.9211, P&L théorique=$-68.11
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.4830, P&L théorique=$-68.11 ⭐

Verdict run 855 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/855/report.json
