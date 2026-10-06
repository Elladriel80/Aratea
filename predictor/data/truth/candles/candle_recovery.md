# Récupérer les prix jetés (bougie 18:00)

Date de mesure : 2026-09-12T17:22:18Z
Aucun chiffre n'est inventé. Champion en ligne inchangé.

## Dataset backfill déjà dans le dépôt

Lignes : 1467. Jours : 62. Du 2026-04-11 au 2026-06-13.
Séries : 6. Capture tamponnée : 18:00 UTC.

Score d'erreur (plus petit = mieux), mêmes 1467 lignes :

- Prix du marché : 0.1243
- Champion (mélange vendor_ensemble) : 0.1300
- Consensus v3 : 0.1364

Le mélange bat le prix : 25 jours sur 62.

## Même univers, règle A contre règle B

Contrats résolus (bin du milieu) : 1535.
Règle A (18:00 pile) : 1496 lignes, 64 jours.
Règle B (dernière bougie 24 h) : 1535 lignes, 64 jours.
Jetées par A : 39.
Récupérées par B : 39.

Part récupérée parmi les jetées de A : 100.0 %.
Taille B / taille A : 1.03.

Score d'erreur du prix, ensemble A (18:00 pile) : 0.1263 (1496 lignes, 64 jours).
Score d'erreur du prix, ensemble B (24 h) : 0.1237 (1535 lignes, 64 jours).

Là où le champion a déjà une chance (dataset backfill) :
- Ensemble A : prix 0.1271, champion 0.1330 (1428 lignes, 62 jours).
- Ensemble B : prix 0.1243, champion 0.1300 (1467 lignes, 62 jours).

## Les 29 séries du catalogue, même fenêtre

Contrats résolus : 7419.
Règle A : 7198 lignes, 64 jours.
Règle B : 7419 lignes, 64 jours.
Récupérées : 221 (100 % des 221 jetées par A). Taille B / A : 1,03.

Score d'erreur du prix : A 0,1320 (7198 lignes) ; B 0,1303 (7419 lignes).
Le champion n'est noté que sur les 6 villes du backfill (mêmes 62 jours).

## Captures live déjà dans le dépôt

Fichiers : 70. Lignes : 16158. Avec un prix : 16038.
Pile à 18:00:00 UTC : 0.

## Décision

Règle B garde 1535 lignes contre 1496 pour la règle A (39 récupérées). Jours sous B : 64 (il en faut 30 pour parler du marché). Là où le champion est noté, son score reste 0.1300 contre 0.1243 pour le prix (62 jours). Le mélange bat le prix 25 jours sur 62. On ne change pas le champion.

Pas de trading avec de l'argent réel.

