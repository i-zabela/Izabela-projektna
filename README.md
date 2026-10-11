# Analiza cen stanovanj v Sloveniji

## Opis projekta

Projekt analizira oglaševane cene stanovanj, ki so naprodaj na portalu
[Moji kvadrati](https://mojikvadrati.com), in preučuje, kateri dejavniki so
povezani s ceno stanovanja oziroma s ceno na kvadratni meter. Obravnavani
dejavniki so:

- regija in kraj,
- četrt (pri stanovanjih v Ljubljani),
- velikost stanovanja,
- obdobje izgradnje stavbe,
- število sob,
- ali gre za novogradnjo.

Analiza temelji na približno 1200 oglasih. Upoštevati je treba, da gre za
oglaševane cene, ki so praviloma nekoliko višje od cen, po katerih se
stanovanja dejansko prodajo.

## Struktura projekta

- `scrape.py` s portala prenese vse strani s seznamom oglasov za prodajo
  stanovanj in jih shrani kot datoteke HTML v mapo `strani`. Med zahtevami
  počaka 30 sekund, kot zahteva `robots.txt` portala. Že prenesene strani
  preskoči, zato je mogoče prekinjen prenos nadaljevati.
- `čiščenje.py` iz shranjenih strani z regularnimi izrazi izlušči podatke o
  posameznih oglasih (regijo, kraj, predel, sobnost, velikost, leto izgradnje
  in ceno), odstrani ponovljene oglase ter oglase iz tujine in vse skupaj
  shrani v datoteko `stanovanja.csv`.
- `priprava.py` vsebuje pomožne funkcije za analizo: nalaganje podatkov in
  izločanje nesmiselnih oglasov, izračun median po skupinah in risanje
  stolpčnih diagramov.
- `analiza_stanovanj.ipynb` je zvezek Jupyter, v katerem je izvedena končna
  analiza s tabelami, grafi in zaključki.
- `stanovanja.csv` vsebuje zajete in očiščene podatke, na katerih temelji
  analiza.
- `requirements.txt` navaja potrebne knjižnice.

## Navodila za uporabo in zagon

1. Klonirajte repozitorij in v terminalu odprite njegovo korensko mapo:

   ```
   git clone https://github.com/i-zabela/Izabela-projektna.git
   cd Izabela-projektna
   ```

2. Namestite potrebne knjižnice:

   ```
    - requests
    - pandas
    - matplotlib
    - notebook
    - numpy
    - seaborn
   ```

3. Če želite prenesti oglase iz dneva, ko zaganjate projekt, zaženite `scrape.py`, ki prenese strani z oglasi. Prenos traja
   približno eno uro, saj program med zahtevami čaka 30 sekund.

   ```
   python scrape.py
   ```

4. Če ste prenašali aktualne podatke, zaženite `čiščenje.py`, ki iz prenesenih strani izdela
   datoteko `stanovanja.csv`.

   ```
   python čiščenje.py
   ```

5. Datoteka `stanovanja.csv` je že v repozitoriju, zato lahko koraka 3 in 4
   izpustite. Če ju izvedete, dobite sveže podatke, zato se lahko rezultati
   nekoliko razlikujejo od opisanih v zvezku.

6. Zaženite Jupyter Notebook:

   ```
   jupyter notebook
   ```

7. Odprite `analiza_stanovanj.ipynb`.

8. Celice izvedite po vrsti ali izberite **Run All**.

Datoteke `priprava.py` ni treba zaganjati posebej, saj vsebuje le funkcije,
ki jih uporablja zvezek. Vse programe zaganjajte iz korenske mape projekta,
saj se datoteka `stanovanja.csv` bere in zapisuje v trenutni mapi. 
*Claude je pomagal pri sestavljanju in urejanju besedila.*
