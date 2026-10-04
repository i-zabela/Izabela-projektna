import pandas as pd
import matplotlib.pyplot as plt

from čiščenje import DATOTEKA_CSV

# naloži podatke in izloči nesmiselne podatke, prav tako ustvari nov stolpec z novogradnjami (zgrajeno po 2024)
def nalozi_podatke(datoteka=DATOTEKA_CSV):
    stanovanja = pd.read_csv(datoteka)
    stanovanja["novogradnja"] = (
        stanovanja["leto_izgradnje"] >= 2024 
    )    
    return stanovanja[
        stanovanja["cena_na_m2"].between(500, 15000)     # cene izven teh dveh se zdijo neresnične in so verjetno napačne zato jih izločim
        & stanovanja["velikost"].between(15, 400)]     # pod 15 in nad 400 ni verjetno

# izračuna mediano cene na kvadrat, mediano cene, mediano velikosti
def mediane(stanovanja, stolpec, najmanj_oglasov=10):     # kraj s samo dvema oglasoma lahko pristane na vrhu lestvice po naključju, zato je minimum 10 stanovanj v npr. kraju
    povzetek = stanovanja.groupby(stolpec, observed=True).agg(
        stevilo_oglasov=("id", "count"),
        mediana_cene_na_m2=("cena_na_m2", "median"),
        mediana_cene=("cena", "median"),
        mediana_velikosti=("velikost", "median"),
    )
    povzetek = povzetek[povzetek["stevilo_oglasov"] >= najmanj_oglasov]     # v povzetek shrani samo tiste, ki vrnejo True (torej tam kjer jih je več od 10) 
    return povzetek.sort_values("mediana_cene_na_m2", ascending=False).round()     # od najdražje do najcenejše mediane cene na kvadrat

# nariše stolpčni diagram mediane cene na kvadrat za vsako vrednost stolpca
def narisi_stolpce(povzetek, naslov, stolpec="mediana_cene_na_m2"):
    """Nariše vodoravni stolpčni diagram mediane cene na m²."""
    ax = povzetek[stolpec].sort_values().plot.barh(       # nariše vodoravni stolpični diagram, stolpci so urejeni po mediani cene na kvadrat
        figsize=(10, 0.4 * len(povzetek) + 1), color="pink"     # višina je odvisna od števila vrstic: 0,4 palca na stolpec in 1 palec za naslov in os
    )
    ax.set_xlabel("mediana cene na m² [EUR]")
    ax.set_ylabel("")
    ax.set_title(naslov)
    for i, vrednost in enumerate(povzetek[stolpec].sort_values()):
        ax.text(vrednost, i, f" {vrednost:,.0f}".replace(",", "."),
                va="center", fontsize=8)
    plt.tight_layout()
    plt.show()












