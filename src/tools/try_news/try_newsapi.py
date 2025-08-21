from newsapi import NewsApiClient
from datetime import datetime, timedelta

API_KEY = "e76c2ad8e531467f8c3403bc67841f67"
newsapi = NewsApiClient(api_key=API_KEY)

data_fim_dt = datetime.now()
data_inicio_dt = data_fim_dt - timedelta(days=30)
data_inicio = data_inicio_dt.strftime("%Y-%m-%d")
data_fim = data_fim_dt.strftime("%Y-%m-%d")


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
print(f"Período: de {data_inicio} até {data_fim}\n")

try:
    todas_as_noticias = newsapi.get_everything(
        q=termo_pesquisa,
        from_param=data_inicio,
        to=data_fim,
        language="pt",
        sort_by="relevancy",
    )

    artigos = todas_as_noticias["articles"]

    if not artigos:
        print("Nenhuma notícia encontrada para este período.")
    else:
        print(
            f"Encontrados {todas_as_noticias['totalResults']} artigos. Mostrando os 5 primeiros com todos os detalhes:\n\n\n"
        )
        for artigo in artigos[:20]:
            titulo = artigo.get("title", "Título não disponível")
            autor = artigo.get("author", "Autor não informado")
            fonte = artigo.get("source", {}).get("name", "Fonte não informada")
            data = artigo.get("publishedAt", "Data não informada")
            descricao = artigo.get("description", "Descrição não disponível")
            link = artigo.get("url", "#")
            imagem_url = artigo.get("urlToImage", "Imagem não disponível")
            conteudo = artigo.get("content", "Conteúdo não disponível")

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
