# Régime ENSO : compte officiel CPC RONI

Généré : 2026-09-12T20:14:47Z.
Série officielle NOAA / NCEP CPC depuis le 1er février 2026 : Relative Oceanic Niño Index (RONI).
Pas de score de prévision. Pas de notation Kalshi température.

## Source et seuils publiés (pas inventés)

- Fichier : `https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt`
- Page : `https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/`
- Annonce officielle (1er février 2026) : `https://www.weather.gov/media/notification/pdf_2026/pns26-05_Relative_ONI.pdf`
- Seuil El Niño (page CPC) : RONI > 0.5 °C
- Seuil La Niña (page CPC) : RONI < -0.5 °C
- Neutre ici : -0.5 ≤ RONI ≤ 0.5
- Épisode colorié (page CPC) : 5 saisons qui se chevauchent d'affilée
- On compte le fichier ASCII (deux décimales). La page web arrondit à une décimale. On ne mélange pas les deux.
- L'ancien ONI reste en ligne pour l'histoire. Il n'est pas compté ici.
- CPC classe des saisons de 3 mois qui se chevauchent, pas une année civile.

## Couverture

- Première saison : DJF 1950
- Dernière saison : JJA 2026
- Années civiles dans le fichier : 77 (1950 à 2026)
- Saisons présentes : 919
- Saisons attendues dans cet intervalle : 919
- Trous au milieu : 0
- Doublons : 0

Aucun trou, aucun doublon dans l'intervalle du fichier.

Année pas finie (ce n'est pas un trou au milieu) :

- 2026 : 7 saisons présentes (dernière JJA 2026), 5 encore absentes (JAS 2026, ASO 2026, SON 2026, OND 2026, NDJ 2026).
- CPC : les toutes dernières valeurs RONI sont une estimation (elles peuvent bouger jusqu'à deux mois).

## Saisons (valeur du seuil ±0,5 °C)

Une saison = 3 mois qui se chevauchent (DJF, JFM, …).

| Phase | Saisons |
|---|---:|
| El Niño (RONI > 0.5) | 239 |
| La Niña (RONI < -0.5) | 229 |
| Neutre | 451 |
| Total | 919 |

## Saisons dans un épisode officiel (5 saisons d'affilée)

| Lecture | Saisons |
|---|---:|
| Dans un El Niño colorié | 218 |
| Dans une La Niña coloriée | 216 |
| Hors épisode (neutre ou run trop court) | 485 |

Épisodes El Niño : 22. Épisodes La Niña : 21.

## Années civiles (le fichier étiquette la saison, pas l'année)

Une année peut avoir les deux. On ne force pas une seule case.

| Lecture | Années |
|---|---:|
| Au moins une saison El Niño | 47 |
| Au moins une saison La Niña | 41 |
| Les deux dans la même année | 17 |
| Seulement neutre | 6 |
| Année incomplète | 1 |

Années avec les deux : 1954, 1964, 1973, 1976, 1983, 1995, 1998, 2005, 2006, 2007, 2009, 2010, 2016, 2018, 2023, 2024, 2026.

Années seulement neutre : 1960, 1961, 1962, 1967, 1981, 1990.

## Épisodes officiels (5 saisons ou plus)

| # | Phase | Début | Fin | Saisons | Pic RONI | Ouvert à la fin |
|---|---|---|---|---:|---:|---|
| 1 | La Niña | DJF 1950 | MJJ 1950 | 6 | -1,19 | non |
| 2 | El Niño | MAM 1951 | DJF 1952 | 10 | +1,04 | non |
| 3 | El Niño | JFM 1953 | JFM 1954 | 13 | +0,94 | non |
| 4 | La Niña | JAS 1955 | DJF 1956 | 6 | -1,40 | non |
| 5 | El Niño | FMA 1957 | MJJ 1958 | 16 | +1,89 | non |
| 6 | El Niño | JJA 1963 | JFM 1964 | 8 | +1,11 | non |
| 7 | La Niña | AMJ 1964 | OND 1964 | 7 | -0,66 | non |
| 8 | El Niño | AMJ 1965 | MAM 1966 | 12 | +1,99 | non |
| 9 | El Niño | SON 1968 | FMA 1969 | 6 | +1,07 | non |
| 10 | La Niña | JAS 1970 | MAM 1971 | 9 | -1,00 | non |
| 11 | El Niño | MAM 1972 | FMA 1973 | 12 | +1,97 | non |
| 12 | La Niña | AMJ 1973 | AMJ 1974 | 13 | -1,91 | non |
| 13 | La Niña | AMJ 1975 | JFM 1976 | 10 | -1,11 | non |
| 14 | El Niño | JJA 1976 | JFM 1977 | 8 | +1,08 | non |
| 15 | El Niño | ASO 1977 | JFM 1978 | 6 | +1,10 | non |
| 16 | El Niño | AMJ 1982 | AMJ 1983 | 13 | +2,40 | non |
| 17 | La Niña | ASO 1983 | JFM 1984 | 6 | -1,10 | non |
| 18 | La Niña | SON 1984 | MJJ 1985 | 9 | -0,93 | non |
| 19 | El Niño | JAS 1986 | NDJ 1987 | 17 | +1,46 | non |
| 20 | La Niña | MAM 1988 | AMJ 1989 | 14 | -1,95 | non |
| 21 | El Niño | AMJ 1991 | JJA 1992 | 15 | +2,12 | non |
| 22 | El Niño | DJF 1993 | MJJ 1993 | 6 | +1,06 | non |
| 23 | El Niño | JJA 1994 | FMA 1995 | 9 | +1,28 | non |
| 24 | La Niña | JAS 1995 | FMA 1996 | 8 | -1,02 | non |
| 25 | El Niño | AMJ 1997 | MAM 1998 | 12 | +2,28 | non |
| 26 | La Niña | JJA 1998 | MJJ 2000 | 24 | -1,61 | non |
| 27 | La Niña | SON 2000 | FMA 2001 | 6 | -0,82 | non |
| 28 | El Niño | JJA 2002 | DJF 2003 | 7 | +1,33 | non |
| 29 | El Niño | JJA 2004 | DJF 2005 | 7 | +0,71 | non |
| 30 | El Niño | ASO 2006 | DJF 2007 | 5 | +0,91 | non |
| 31 | La Niña | JAS 2007 | AMJ 2008 | 10 | -1,73 | non |
| 32 | La Niña | OND 2008 | FMA 2009 | 5 | -0,96 | non |
| 33 | El Niño | ASO 2009 | FMA 2010 | 7 | +1,50 | non |
| 34 | La Niña | MJJ 2010 | AMJ 2011 | 12 | -1,63 | non |
| 35 | La Niña | ASO 2011 | JFM 2012 | 6 | -1,02 | non |
| 36 | El Niño | FMA 2015 | MAM 2016 | 14 | +2,25 | non |
| 37 | La Niña | JJA 2016 | DJF 2017 | 7 | -0,96 | non |
| 38 | La Niña | ASO 2017 | MAM 2018 | 8 | -1,14 | non |
| 39 | El Niño | SON 2018 | MAM 2019 | 7 | +0,82 | non |
| 40 | La Niña | AMJ 2020 | FMA 2023 | 35 | -1,46 | non |
| 41 | El Niño | JJA 2023 | JFM 2024 | 8 | +1,42 | non |
| 42 | La Niña | JAS 2024 | FMA 2025 | 8 | -1,10 | non |
| 43 | La Niña | JAS 2025 | JFM 2026 | 7 | -1,04 | non |

Runs au-dessus du seuil mais trop courts pour un épisode (moins de 5 saisons) :

| Phase | Début | Fin | Saisons |
|---|---|---|---:|
| El Niño | NDJ 1958 | FMA 1959 | 4 |
| El Niño | JJA 1968 | JJA 1968 | 1 |
| El Niño | ASO 1969 | NDJ 1969 | 4 |
| El Niño | MJJ 1977 | MJJ 1977 | 1 |
| El Niño | SON 1979 | DJF 1980 | 4 |
| El Niño | DJF 1991 | JFM 1991 | 2 |
| El Niño | OND 2014 | DJF 2015 | 3 |
| El Niño | MJJ 2026 | JJA 2026 | 2 |
| La Niña | JAS 1954 | ASO 1954 | 2 |
| La Niña | MJJ 1955 | MJJ 1955 | 1 |
| La Niña | OND 1974 | OND 1974 | 1 |
| La Niña | MAM 1984 | MJJ 1984 | 3 |
| La Niña | NDJ 2005 | FMA 2006 | 4 |
| La Niña | DJF 2013 | JFM 2013 | 2 |

## Table année par année

| Année | Saisons dans le fichier | El Niño | La Niña | Neutre | Mélange |
|---|---:|---:|---:|---:|---|
| 1950 | 12 | 0 | 6 | 6 | La Niña |
| 1951 | 12 | 9 | 0 | 3 | El Niño |
| 1952 | 12 | 1 | 0 | 11 | El Niño |
| 1953 | 12 | 11 | 0 | 1 | El Niño |
| 1954 | 12 | 2 | 2 | 8 | les deux |
| 1955 | 12 | 0 | 6 | 6 | La Niña |
| 1956 | 12 | 0 | 1 | 11 | La Niña |
| 1957 | 12 | 10 | 0 | 2 | El Niño |
| 1958 | 12 | 7 | 0 | 5 | El Niño |
| 1959 | 12 | 3 | 0 | 9 | El Niño |
| 1960 | 12 | 0 | 0 | 12 | neutre |
| 1961 | 12 | 0 | 0 | 12 | neutre |
| 1962 | 12 | 0 | 0 | 12 | neutre |
| 1963 | 12 | 6 | 0 | 6 | El Niño |
| 1964 | 12 | 2 | 7 | 3 | les deux |
| 1965 | 12 | 8 | 0 | 4 | El Niño |
| 1966 | 12 | 4 | 0 | 8 | El Niño |
| 1967 | 12 | 0 | 0 | 12 | neutre |
| 1968 | 12 | 4 | 0 | 8 | El Niño |
| 1969 | 12 | 7 | 0 | 5 | El Niño |
| 1970 | 12 | 0 | 5 | 7 | La Niña |
| 1971 | 12 | 0 | 4 | 8 | La Niña |
| 1972 | 12 | 9 | 0 | 3 | El Niño |
| 1973 | 12 | 3 | 8 | 1 | les deux |
| 1974 | 12 | 0 | 6 | 6 | La Niña |
| 1975 | 12 | 0 | 8 | 4 | La Niña |
| 1976 | 12 | 6 | 2 | 4 | les deux |
| 1977 | 12 | 7 | 0 | 5 | El Niño |
| 1978 | 12 | 2 | 0 | 10 | El Niño |
| 1979 | 12 | 3 | 0 | 9 | El Niño |
| 1980 | 12 | 1 | 0 | 11 | El Niño |
| 1981 | 12 | 0 | 0 | 12 | neutre |
| 1982 | 12 | 8 | 0 | 4 | El Niño |
| 1983 | 12 | 5 | 4 | 3 | les deux |
| 1984 | 12 | 0 | 8 | 4 | La Niña |
| 1985 | 12 | 0 | 6 | 6 | La Niña |
| 1986 | 12 | 5 | 0 | 7 | El Niño |
| 1987 | 12 | 12 | 0 | 0 | El Niño |
| 1988 | 12 | 0 | 9 | 3 | La Niña |
| 1989 | 12 | 0 | 5 | 7 | La Niña |
| 1990 | 12 | 0 | 0 | 12 | neutre |
| 1991 | 12 | 10 | 0 | 2 | El Niño |
| 1992 | 12 | 7 | 0 | 5 | El Niño |
| 1993 | 12 | 6 | 0 | 6 | El Niño |
| 1994 | 12 | 6 | 0 | 6 | El Niño |
| 1995 | 12 | 3 | 5 | 4 | les deux |
| 1996 | 12 | 0 | 3 | 9 | La Niña |
| 1997 | 12 | 8 | 0 | 4 | El Niño |
| 1998 | 12 | 4 | 6 | 2 | les deux |
| 1999 | 12 | 0 | 12 | 0 | La Niña |
| 2000 | 12 | 0 | 9 | 3 | La Niña |
| 2001 | 12 | 0 | 3 | 9 | La Niña |
| 2002 | 12 | 6 | 0 | 6 | El Niño |
| 2003 | 12 | 1 | 0 | 11 | El Niño |
| 2004 | 12 | 6 | 0 | 6 | El Niño |
| 2005 | 12 | 1 | 1 | 10 | les deux |
| 2006 | 12 | 4 | 3 | 5 | les deux |
| 2007 | 12 | 1 | 5 | 6 | les deux |
| 2008 | 12 | 0 | 7 | 5 | La Niña |
| 2009 | 12 | 4 | 3 | 5 | les deux |
| 2010 | 12 | 3 | 7 | 2 | les deux |
| 2011 | 12 | 0 | 9 | 3 | La Niña |
| 2012 | 12 | 0 | 2 | 10 | La Niña |
| 2013 | 12 | 0 | 2 | 10 | La Niña |
| 2014 | 12 | 2 | 0 | 10 | El Niño |
| 2015 | 12 | 11 | 0 | 1 | El Niño |
| 2016 | 12 | 4 | 6 | 2 | les deux |
| 2017 | 12 | 0 | 5 | 7 | La Niña |
| 2018 | 12 | 3 | 4 | 5 | les deux |
| 2019 | 12 | 4 | 0 | 8 | El Niño |
| 2020 | 12 | 0 | 8 | 4 | La Niña |
| 2021 | 12 | 0 | 12 | 0 | La Niña |
| 2022 | 12 | 0 | 12 | 0 | La Niña |
| 2023 | 12 | 6 | 3 | 3 | les deux |
| 2024 | 12 | 2 | 5 | 5 | les deux |
| 2025 | 12 | 0 | 8 | 4 | La Niña |
| 2026 | 7 | 2 | 2 | 3 | les deux |

## Mois de chaque saison CPC

| Saison | Mois |
|---|---|
| DJF | Dec Jan Feb |
| JFM | Jan Feb Mar |
| FMA | Feb Mar Apr |
| MAM | Mar Apr May |
| AMJ | Apr May Jun |
| MJJ | May Jun Jul |
| JJA | Jun Jul Aug |
| JAS | Jul Aug Sep |
| ASO | Aug Sep Oct |
| SON | Sep Oct Nov |
| OND | Oct Nov Dec |
| NDJ | Nov Dec Jan |

DJF d'une année Y contient décembre de l'année Y-1. NDJ d'une année Y contient janvier de l'année Y+1. C'est la convention CPC, pas une année inventée.

Champion Kalshi inchangé. Pas de trading réel. Pas SEAS5. Pas C3S.
