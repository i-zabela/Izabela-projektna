import requests
import time
from pathlib import Path

OSNOVNI_URL = "https://mojikvadrati.com"
URL_SCROLLA = OSNOVNI_URL + "/engine/call/project_model/ajax_get_items_list"
FILTER = "prodaja-stanovanja"
URL_FILTRA = f"{OSNOVNI_URL}/nepremicnine/{FILTER}"
MAPA_STRANI = Path(__file__).parent / "strani"     # pot do mape s stranmi

# da ne dobim napake 403, moram dodati glave
GLAVE = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "sl-SI,sl;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
}


# to naredim, da strežnik nastavi piškotke
def zacni_sejo(glave=GLAVE, domaca_stran=URL_FILTRA):    # nastavim privzete vrednosti
    seja = requests.Session()     # ustvari objekt seja
    seja.headers.update(glave)     # doda glavo 
    seja.get(domaca_stran, timeout=30).raise_for_status()      # gre na domačo stran in nastavi piškotk4e, ki jih pošilja pri vseh naslednjih zahtevah
    return seja

# pridobi dano stran z oglasi in vrne njen html
def pridobi_stran(seja, stran):
    # prebrano iz Payload (Pot: F12 -> Network -> Payload)
    podatki = {
        "options": "{}",
        "order": "?sort=created_lt-desc",
        "currenturl": URL_FILTRA,
        "language": "sl",
        "page": stran,
        "filter": FILTER,
        "items_list_variation": "default",
    }
    odziv = seja.post(URL_SCROLLA, data=podatki, timeout=30)    # pošlje strežniku zahtevek HTTP POST in vrne njegov odgovor kot objekt Response, ki je shranjen kot odziv
    odziv.raise_for_status()    # preveri, če je statusna koda 200, če ni sproži izjemo pri kodah 400 in več
    rezultat = odziv.json()["result"]     # vzela ključ iz JSON odgovora, ki vsebuje html in meta podatke
    return rezultat["html"]     # vrne html 
    
def pot_do_strani(stran):
    """Vrne pot, na katero shranimo dano stran."""
    return MAPA_STRANI / f"stran_{stran:03}.html"

def prenesi_vse(najvec_strani=300):
    """Prenese vse strani z oglasi, ki še niso shranjene."""
    MAPA_STRANI.mkdir(parents=True, exist_ok=True)
    seja = zacni_sejo()
    for stran in range(1, najvec_strani + 1):
        pot = pot_do_strani(stran)
        if pot.exists():
            continue
        time.sleep(30)
        html = pridobi_stran(seja, stran)
        if "list-item-body" not in html:
            print("Ni več oglasov, prenos je končan.")
            return
        with open(pot, "w", encoding="utf-8") as p:
            p.write(html)


if __name__ == "__main__":
    prenesi_vse()