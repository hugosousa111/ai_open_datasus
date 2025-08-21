import os
from langchain_community.utilities import GoogleSerperAPIWrapper
import pprint

os.environ["SERPER_API_KEY"] = "33f551dcbabb9a7a2e361500467514dcc8461c2f"

termos_de_busca = [
    "srag",
    "srag brasil",
    "síndrome respiratória aguda grave",
    "síndrome respiratória",
    "surto respiratório brasil",
    "influenza brasil",
    "gripe brasil",
    "covid-19 brasil",
    "covid brasil",
]

search = GoogleSerperAPIWrapper(type="news", tbs="qdr:m", gl="br", hl="pt")

results = search.results(query=termos_de_busca)

pprint.pp(results["news"])
