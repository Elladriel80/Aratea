# Ville, forêt et eau autour de la station

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Question : une ville, une forêt ou de l'eau changent-elles la température, et à quelle distance de la station ?

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec de l'argent réel. Aucun chiffre n'a été inventé.

## Ce que ça mesure

Ville = habitants au km². Pas le nombre de bâtiments.

Forêt = part du sol qui est verte. Pas le nombre d'arbres sur une carte.

Eau = part du sol qui est de l'eau (mer, lac, fleuve). Pas le nombre de rivières sur une carte.

On a regardé 1, 2, 5, 10 et 20 km autour du vrai point des 18 stations. Habitants : fichier public WorldPop 2020. Vert et eau : carte publique ESA 2021. Températures : le fichier officiel déjà utilisé pour le siècle.

## Quelques chiffres vrais

New York, à 5 km : 16653 habitants / km².
Denver (aéroport), à 5 km : 0 habitant / km².
Boston, à 20 km : 35 % d'eau.
Denver, à 20 km : 1 % d'eau.
Phoenix, à 5 km : 10 % de sol vert.

Ça suffit à dire : ici c'est une ville, ici c'est près de l'eau, ici c'est sec. Pour la mutuelle, un terrain près d'un lac n'est pas un terrain en ville.

## Quel rayon a un effet ?

L'eau, oui. Surtout à 20 km. Déjà visible à 10 km et à 5 km. À 1 km, presque rien.

Plus il y a d'eau autour, plus le jour et la nuit se ressemblent (ordre à 20 km : -0,88 ; à 10 km : -0,75 ; à 5 km : -0,70 ; à 1 km : -0,37).

En clair : Boston ou San Francisco (beaucoup de mer) n'ont pas le même écart jour-nuit que Denver ou Phoenix (presque pas d'eau). Le 20 km est le plus net.

La ville (habitants), non. Ranger les 18 stations de la plus habitée à la moins habitée ne range pas les nuits (à 5 km, ordre 0,10, trop faible). Ces 18 points sont surtout des aéroports, pas le centre-ville. À 1 km, presque tous sont vides. C'est la piste d'atterrissage.

La forêt (sol vert), non. Ranger les stations de la plus verte à la moins verte ne range pas les jours les plus chauds (à 5 km, ordre -0,07, trop faible).

On ne force pas une histoire que les 18 points ne tiennent pas.

## Est-ce que ça aide les paris du jour ?

Mélange déjà corrigé ville par ville : 0,1154.
Meilleur essai avec les densités (rayon 20 km) : 0,1229.

Ça n'aide pas les paris du jour. On s'y attendait. Corriger chaque ville avec son propre écart marche déjà. Ajouter ville, forêt ou eau par-dessus ne gagne pas. L'ancien essai (compter les bâtiments sur une carte) avait déjà échoué.

Prix du marché, la veille (62 jours, mêmes contrats) : 0,1253.
Densités sur ces mêmes contrats : 0,1437.
Les densités ne battent pas le marché.

## Décision

On ne change pas le modèle en ligne. Les densités ne battent pas le mélange corrigé ville par ville (0,1229 contre 0,1154 au meilleur rayon, 36 jours). Sur les contrats avec un prix (la veille, 62 jours) : densités 0,1437 contre marché 0,1253. L'eau à 20 km est le lien le plus net avec l'écart entre le jour et la nuit. Utile pour décrire un lieu (mutuelle), pas pour remplacer la correction ville par ville.

Les tableaux sont dans `data/truth/density/density_report.md`.
Pour relancer : `python scripts/eval_land_density.py --from-json data/truth/density/densities.json`

Pas de changement du texte du site. Pas de trading réel.
