import csv
import re

from scrape import MAPA_STRANI

DATOTEKA_CSV = "stanovanja.csv"

# Primer oglasa:
# <a href="https://mojikvadrati.com/nepremicnina/541277-prodaja-..."
#    class="list-item-body"><div class="cost green">157.800 €</div>
#    <div class="location">Podravska, Maribor, Betnava</div>
#    <div class="detail-category">Stanovanje • 2-sobno • 52.6 m2 • 1980</div>...

# v modrem so imena skupin
VZOREC_OGLASA = re.compile(     # re.compile() pretvori regularni izraz v objekt vzorca. To je uporabno, kadar isti vzorec uporabiš večkrat, saj ga Python ne prevaja vsakič znova.  
    r'<a href="(?P<povezava>[^"]*/nepremicnina/(?P<id>\d+)-[^"]*)"\s*'     # [^"]*: poljubno znakov, ki niso narekovaj.
    r'class="list-item-body">\s*'
    r'<div class="cost[^"]*">(?P<cena>.*?)</div>\s*'     # .*? je nepožrešen: ujame čim manj, torej se ustavi pri prvem </div>. Brez ? bi požrl vse do zadnjega </div> na strani.
    r'<div class="location">(?P<lokacija>.*?)</div>\s*'
    r'<div class="detail-category">(?P<opis>.*?)</div>',
    flags=re.DOTALL,    # brez te zastavice "." ne ujame preloma vrstice
)
VZOREC_CENE = re.compile(r"^([\d.]+) €")
VZOREC_VELIKOSTI = re.compile(r"^([\d.]+) m2$")
VZOREC_LETA = re.compile(r"^\d{4}$")     # \d{4}: točno štiri števke. ^...$: in nič drugega
VZOREC_SOBNOSTI = re.compile(r"^(\d)(?:,(5))?")    # (?:...) neobvezen del

# portal objavlja tudi oglase iz tujine (Hrvaška, Dubaj …), ki jih izločimo
SLOVENSKE_REGIJE = {
    "Ljubljana", "Ljubljana okolica", "Gorenjska", "Goriška",
    "Obalno - kraška", "Notranjsko - kraška", "Primorsko - notranjska",
    "Savinjska", "Podravska", "Pomurska", "Koroška",
    "Jugovzhodna Slovenija", "Posavska", "Spodnjeposavska", "Zasavska",
}

STOLPCI = (
    "id", "regija", "kraj", "predel", "sobnost", "st_sob", "velikost",
    "leto_izgradnje", "cena", "cena_na_m2", "povezava",
)

# vrne število brez pike, ki jo sicer dojema kot decimalko
def v_stevilo(niz):
    return int(niz.replace(".", "")) 

# iz besedila izlušči samo številko cene
def preberi_ceno(besedilo):
    ujemanje = VZOREC_CENE.match(besedilo)     # poišče vzorce v besedilu
    return v_stevilo(ujemanje[1]) if ujemanje else None     # [1] je zato da dobim samo število brez €


# lokacijo 'regija, občina, predel' razdeli na dele
def razcleni_lokacijo(lokacija):
    deli = [delec.strip() for delec in lokacija.split(",")]     # želim odstraniti še presledke ob besedi
    deli += [None] * (3 - len(deli))
    regija, kraj, predel = deli[:3]
    if regija == "Ljubljana":       # Pri Ljubljani je drugi del četrt (npr. 'Ljubljana, Šiška, Dravlje'), zato za občino vzamemo Ljubljano, za predel pa četrt.
        return regija, "Ljubljana", kraj    
    return regija, kraj, predel

# iz opisa 'Stanovanje • 2-sobno • 52.6 m2 • 1980' vrne sobnost, velikost in leto izgradnje (manjkajoči podatki so None)
def razcleni_opis(opis):
    sobnost = velikost = leto = None
    for delec in (delec.strip() for delec in opis.split("•")[1:]):      # od prvega naprej, ker smo že prej določili, da gledamo samo stanovanja
        ujemanje = VZOREC_VELIKOSTI.match(delec)
        if ujemanje:
            velikost = float(ujemanje[1])     # [1] da dobimo samo število, brez m2
        elif VZOREC_LETA.match(delec):
            leto = int(delec)
        elif "sob" in delec or delec.lower() == "garsonjera":     # "sob" je del besede, ki je skupen vsem oznakam sobnosti (večsobno, 4 sobe...)
            sobnost = delec
    return sobnost, velikost, leto

# sobnosti priredi število 
def pretvori_sobnost(sobnost):
    if sobnost == None:
        return None
    if sobnost.lower() == "garsonjera": 
        return 0.5
    ujemanje = VZOREC_SOBNOSTI.match(sobnost) 
    if ujemanje is None:
        return None
    return int(ujemanje[1]) + (0.5 if ujemanje[2] else 0)     # za prvo skupino doda celo sobo, za drugo pa pol če le-ta obstaja

# iz ujemanja z vzorcem oglasa vrne slovar s podatki o oglasu ali None, če oglasu manjka cena ali velikost
def izlusci_oglas(ujemanje):
    cena = preberi_ceno(ujemanje["cena"])
    if cena is None:
        return None
    regija, kraj, predel = razcleni_lokacijo(ujemanje["lokacija"])
    sobnost, velikost, leto = razcleni_opis(ujemanje["opis"])
    if velikost is None:
        return None
    return {
        "id": int(ujemanje["id"]),
        "regija": regija,
        "kraj": kraj,
        "predel": predel,
        "sobnost": sobnost,
        "st_sob": pretvori_sobnost(sobnost),
        "velikost": velikost,
        "leto_izgradnje": leto,
        "cena": cena,
        "cena_na_m2": round(cena / velikost),
        "povezava": ujemanje["povezava"],
    }

# prebere vse shranjene strani in vrne seznam slovenskih oglasov brez ponovitev
def izlusci_vse(mapa=MAPA_STRANI):
    oglasi = {}    # ustvarimo prazen slovar, kamor bomo shranjevali oglase, da ne bo ponovitev
    for pot in sorted(mapa.glob("*.html")):    # prebere vse datoteke z html končnico v mapi MAPA_STRANI in jih uredi po abecedi
        vsebina = pot.read_text(encoding="utf-8")    # read_text() prebere vsebino datoteke kot niz
        for ujemanje in VZOREC_OGLASA.finditer(vsebina):    # finditer() pa vrne generator, ki vrne ujemanja z vzorcem v nizu
            oglas = izlusci_oglas(ujemanje)
            if oglas is None:
                continue
            if oglas["regija"] in SLOVENSKE_REGIJE:
                oglasi[oglas["id"]] = oglas
    return list(oglasi.values())

# shrani seznam oglasov v datoteko CSV
def shrani_csv(oglasi, datoteka=DATOTEKA_CSV):
    with open(datoteka, "w", encoding="utf-8", newline="") as f:
        pisec = csv.DictWriter(f, fieldnames=STOLPCI)
        pisec.writeheader()
        pisec.writerows(oglasi)

def main():
    oglasi = izlusci_vse()
    shrani_csv(oglasi)
    print(f"Shranjenih {len(oglasi)} oglasov v {DATOTEKA_CSV}.")
        
if __name__ == "__main__":
    main()