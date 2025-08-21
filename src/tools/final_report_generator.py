import json
import logging
from pathlib import Path

from utils.utils import setup_logging, load_config
import os
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import navy, black, HexColor
from reportlab.lib.units import inch


class FinalReportGeneratorTool:
    """
    Classe responsável por gerar o relatório final em HTML a partir de um template,
    substituindo placeholders por dados de arquivos JSON e Markdown.
    """

    def __init__(
        self,
        metadata_file_path,
        periods_file_path,
        metrics_file_path,
        report_file_path,
        last_30_days_plot_file_path,
        last_12_months_plot_file_path,
    ):
        """
        Inicializa o gerador de relatório, configura o logging e carrega
        as configurações a partir do arquivo parameters.yaml.
        """
        setup_logging()
        self.metadata_file_path = metadata_file_path
        self.periods_file_path = periods_file_path
        self.metrics_file_path = metrics_file_path
        self.report_file_path = report_file_path
        self.last_30_days_plot_file_path = last_30_days_plot_file_path
        self.last_12_months_plot_file_path = last_12_months_plot_file_path
        try:
            config = load_config()
            self.report_cfg = config["final_report_config"]

            base_path = Path.cwd()
            self.paths = {
                key: base_path / Path(path_str)
                for key, path_str in self.report_cfg["paths"].items()
            }

        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"Falha ao inicializar o FinalReportGeneratorTool devido a erro de configuração. Detalhes: {e}"
            )
            raise ValueError("Erro de configuração impede a continuação.") from e

    def _load_json(self, file_path: Path) -> dict:
        """Carrega dados de um arquivo JSON. (Método privado)"""
        logging.info(f"Carregando arquivo JSON de: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Erro ao carregar o arquivo JSON {file_path}: {e}")
            raise

    def _read_text(self, file_path: Path) -> str:
        """Lê o conteúdo de um arquivo de texto. (Método privado)"""
        logging.info(f"Lendo arquivo de texto de: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError as e:
            logging.error(f"Erro ao ler o arquivo de texto {file_path}: {e}")
            raise

    def _write_text(self, file_path: Path, content: str):
        """Escreve conteúdo em um arquivo de texto. (Método privado)"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logging.info(f"Arquivo salvo com sucesso em: {file_path}")
        except IOError as e:
            logging.error(f"Não foi possível escrever o arquivo em {file_path}: {e}")
            raise

    def _get_replacements(self) -> dict:
        """Coleta todos os dados e monta um dicionário de substituições. (Método privado)"""
        logging.info("Coletando dados para o relatório...")

        metadata = self._load_json(self.metadata_file_path)
        metrics = self._load_json(self.metrics_file_path)
        periods = self._load_json(self.periods_file_path)

        report_md_content = self._read_text(self.report_file_path)

        replacements = {
            "[raw_auto_metadata.update_date]": metadata.get("update_date", ""),
            "[raw_auto_metadata.date_last_file]": metadata.get("date_last_file", ""),
            "[path.report.md]": report_md_content,
            "[path.last_12_months.png]": self.last_12_months_plot_file_path,
            "[path.last_30_days.png]": self.last_30_days_plot_file_path,
        }

        for category, values in metrics.items():
            for key, value in values.items():
                replacements[f"[{category}.{key}]"] = str(value)

        for period, dates in periods.items():
            for key, date_value in dates.items():
                replacements[f"[{period}.{key}]"] = str(date_value)

        logging.info("Dicionário de substituições criado com sucesso.")
        return replacements

    def _gerar_pdf_de_html(self, html_content, output_filename="relatorio.pdf"):
        """
        Analisa um conteúdo HTML, extrai os dados de um relatório e gera um PDF.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            topMargin=inch,
            bottomMargin=inch,
            leftMargin=inch,
            rightMargin=inch,
        )
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="TitleStyle",
                fontName="Helvetica-Bold",
                fontSize=22,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=navy,
            )
        )
        styles.add(
            ParagraphStyle(
                name="HeaderInfo",
                fontName="Helvetica-Oblique",
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=black,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H2Style",
                fontName="Helvetica-Bold",
                fontSize=16,
                spaceBefore=20,
                spaceAfter=15,
                textColor=navy,
                borderBottomWidth=1,
                borderBottomColor=navy,
                paddingBottom=5,
            )
        )
        styles.add(
            ParagraphStyle(
                name="H3Style",
                fontName="Helvetica-Bold",
                fontSize=12,
                spaceBefore=10,
                spaceAfter=10,
                textColor=HexColor("#004a99"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyTextStyle",
                fontName="Helvetica",
                fontSize=11,
                alignment=TA_JUSTIFY,
                leading=14,
            )
        )
        styles.add(
            ParagraphStyle(
                name="ListItemStyle",
                fontName="Helvetica",
                fontSize=11,
                leftIndent=20,
                spaceAfter=5,
            )
        )

        story = []

        title = soup.find("h1").get_text(strip=True)
        story.append(Paragraph(title, styles["TitleStyle"]))

        header_info = (
            soup.find("p", class_="info-header")
            .get_text(separator="\n", strip=True)
            .replace("\n", "<br/>")
        )
        story.append(Paragraph(header_info, styles["HeaderInfo"]))

        metrics_section = soup.find("section", id="metrics")
        story.append(
            Paragraph(
                metrics_section.find("h2").get_text(strip=True), styles["H2Style"]
            )
        )

        for h3 in metrics_section.find_all("h3"):
            story.append(Paragraph(h3.get_text(strip=True), styles["H3Style"]))
            metric_cards = h3.find_next_sibling("div", class_="metrics-grid").find_all(
                "div", class_="metric-card"
            )
            table_data = []
            for card in metric_cards:
                key = card.find("strong").get_text(strip=True)
                value = card.find("span").get_text(strip=True)
                table_data.append(
                    [
                        Paragraph(key, styles["BodyTextStyle"]),
                        Paragraph(value, styles["BodyTextStyle"]),
                    ]
                )
            table = Table(table_data, colWidths=[doc.width / 2.0] * 2)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#eef7ff")),
                        ("GRID", (0, 0), (-1, -1), 1, black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("PADDING", (0, 0), (-1, -1), 10),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 15))

        periods_section = soup.find("section", id="periods")
        story.append(PageBreak())
        story.append(
            Paragraph(
                periods_section.find("h2").get_text(strip=True), styles["H2Style"]
            )
        )

        for li in periods_section.find_all("li"):
            story.append(
                Paragraph(f"• {li.get_text(strip=True)}", styles["ListItemStyle"])
            )

        graphs_section = soup.find("section", id="graphs")
        story.append(PageBreak())
        story.append(
            Paragraph(graphs_section.find("h2").get_text(strip=True), styles["H2Style"])
        )

        for graph_container in graphs_section.find_all("div", class_="graph-container"):
            title_tag = graph_container.find("h3")
            img_tag = graph_container.find("img")

            if title_tag and img_tag:
                story.append(
                    Paragraph(title_tag.get_text(strip=True), styles["H3Style"])
                )
                original_path = img_tag.get("src")
                clean_path = ""
                if "data/" in original_path:
                    start_index = original_path.find("data/")
                    clean_path = original_path[start_index:]
                clean_path = clean_path.replace("/", os.path.sep)

                if os.path.exists(clean_path):
                    img = Image(
                        clean_path, width=doc.width * 0.9, height=doc.width * 0.9 * 0.6
                    )
                    story.append(img)
                    story.append(Spacer(1, 15))
                else:
                    error_message = (
                        f"<b>[Imagem não encontrada no caminho: {clean_path}]</b>"
                    )
                    story.append(Paragraph(error_message, styles["BodyTextStyle"]))

        report_text_section = soup.find("section", id="report-text")
        story.append(PageBreak())
        story.append(
            Paragraph(
                report_text_section.find("h2").get_text(strip=True), styles["H2Style"]
            )
        )

        markdown_content = report_text_section.find(
            "div", class_="markdown-content"
        ).get_text("\n", strip=True)

        for line in markdown_content.split("\n"):
            if line.strip():
                if line.startswith("**"):
                    line = f"<b>{line.replace('**', '')}</b>"
                story.append(Paragraph(line, styles["BodyTextStyle"]))
                story.append(Spacer(1, 5))

        try:
            doc.build(story)
            print(f"Relatório '{output_filename}' gerado com sucesso!")
        except Exception as e:
            print(f"Ocorreu um erro ao gerar o PDF: {e}")

    def run_generation_process(self) -> str | None:
        """
        Orquestra a leitura, substituição e escrita do relatório.
        Retorna o caminho do arquivo gerado em caso de sucesso ou None em caso de falha.
        """
        logging.info(
            "--- Iniciando processo de geração do relatório final (via Tool) ---"
        )

        try:
            html_template_content = self._read_text(self.paths["template_html"])

            replacements = self._get_replacements()

            final_html_content = html_template_content
            for placeholder, value in replacements.items():
                final_html_content = final_html_content.replace(placeholder, value)

            logging.info("Substituições no template HTML foram concluídas.")

            output_path = self.paths["output_html"]

            self._write_text(output_path, final_html_content)
            self._gerar_pdf_de_html(final_html_content)

            logging.info(
                "--- Processo de geração do relatório finalizado com sucesso ---"
            )
            return str(output_path)

        except (FileNotFoundError, KeyError) as e:
            logging.error(
                f"FALHA: Falha ao gerar o relatório. Verifique os caminhos e a estrutura dos arquivos. Erro: {e}"
            )
            return None
        except Exception as e:
            logging.error(
                f"FALHA: Ocorreu um erro inesperado durante a geração do relatório: {e}",
                exc_info=True,
            )
            return None
