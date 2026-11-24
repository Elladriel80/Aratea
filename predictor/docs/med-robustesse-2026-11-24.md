# Aratea : la petite avance Méditerranée tient-elle ? (24 novembre 2026)

## La question

Le 7 octobre, la prévision du centre météo européen (ECMWF) faisait un peu mieux que la moyenne habituelle pour dire si une saison serait plus sèche que d'habitude autour de la Méditerranée. Score 0,063, juste au-dessus de notre seuil de 0,05. On a vérifié si cette avance est solide.

## La réponse courte

Non, elle n'est pas solide. Elle ressemble surtout à de la chance.

- Le 0,063 peut très bien être un vrai 0. La fourchette de confiance va de -0,29 à +0,42.
- Il marche sur 2005 à 2017 (+0,30) mais pas sur 1993 à 2004 (-0,15).
- Il vient seulement des prévisions faites le 1er jour du mois prévu. Dès qu'on prévoit un mois à l'avance, il n'y a plus rien.
- Une vraie prévision de saison, faite le premier jour de la saison, fait moins bien que la moyenne habituelle (-0,40).
- Avec d'autres seuils (très sec, sec, humide, très humide), ça ne marche pas non plus.
- Le mélange de 5 centres météo ne fait pas mieux.

## Le seul indice qui vaut le coup

L'hiver (décembre, janvier, février), avec une prévision faite le 1er décembre. Score 0,54. Quand elle annonce un hiver sec, il est sec 85 fois sur 100. Quand elle ne l'annonce pas, il est sec 9 fois sur 100.

Mais attention :
- On n'a que 24 hivers. La fourchette va de -0,07 à 1,0, donc ce n'est pas prouvé.
- Si la prévision est faite le 1er novembre, l'avance disparaît.
- On a testé 29 découpages. Sur un petit découpage comme celui-là, la chance seule donne un bon score environ 4 fois sur 10. Trouver 4 bons découpages sur 29 n'a rien d'étonnant.

C'est donc une piste à creuser, pas une avance prouvée.

## Ce qu'il faudrait pour en avoir le coeur net

1. Récupérer les prévisions d'hiver récentes (2017 à 2025), que le modèle n'a jamais vues, et regarder si l'hiver marche encore.
2. Utiliser toutes les prévisions individuelles du modèle (pas seulement leur moyenne) pour donner une vraie probabilité au lieu d'un simple oui ou non.

Ces deux étapes demandent un nouveau téléchargement chez Copernicus. Rien n'a été téléchargé aujourd'hui.

## Ce qui ne change pas

- Le champion pour les températures Kalshi reste le prix du marché.
- Aucun argent réel. Les paris papier restent à l'arrêt.
- La modification du 7 octobre (PR 260) n'est pas fusionnée.

Chiffres complets : `predictor/data/truth/c3s_ab/MED_ROBUSTNESS.md` et `predictor/data/truth/c3s_ab/MED_ROBUSTNESS.json`.
