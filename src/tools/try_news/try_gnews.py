from gnews import GNews
from datetime import datetime, timedelta

google_news = GNews(language="pt", country="BR")

data_fim_dt = datetime.now()
data_inicio_dt = data_fim_dt - timedelta(days=30)

google_news.start_date = data_inicio_dt
google_news.end_date = data_fim_dt

termo_pesquisa = (
    '"srag" OR '
    '"srag brasil" OR '
    '"síndrome respiratória aguda grave" OR '
    '"síndrome respiratória" OR '
    '"surto respiratório brasil" OR '
    '"influenza brasil" OR '
    '"gripe brasil" OR '
    '"covid-19 brasil" OR '
    '"covid brasil"'
)

print(f"Buscando por: '{termo_pesquisa}'")
print(
    f"Período: de {data_inicio_dt.strftime('%Y-%m-%d')} até {data_fim_dt.strftime('%Y-%m-%d')}\n"
)

try:
    artigos = google_news.get_news(termo_pesquisa)

    if not artigos:
        print("Nenhuma notícia encontrada para este período.")
    else:
        print(
            f"Encontrados {len(artigos)} artigos. Mostrando os 5 primeiros com todos os detalhes disponíveis:\n\n\n"
        )

        for artigo in artigos[:5]:
            titulo = artigo.get("title", "Título não disponível")

            autor = "Autor não informado (não disponível via gnews)"

            fonte = artigo.get("publisher", {}).get("title", "Fonte não informada")

            data = artigo.get("published date", "Data não informada")

            descricao = artigo.get("description", "Descrição não disponível")

            link = artigo.get("url", "#")

            imagem_url = "Imagem não disponível via gnews"
            conteudo = "Conteúdo não disponível via gnews"

            print(f"Título: {titulo}")
            print(f"Autor: {autor}")
            print(f"Fonte: {fonte}")
            print(f"Data: {data}")
            print(f"Descrição: {descricao}")
            print(f"Link da Imagem: {imagem_url}")
            print(f"Trecho do Conteúdo: {conteudo}")
            print(f"Link do Artigo: {link}")
            print("-" * 40)
            print("\n\n\n")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
