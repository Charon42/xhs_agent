import argparse
import json
from datetime import datetime
from pathlib import Path

from config import DEFAULT_OUTPUT_DIR, DEFAULT_STORAGE_STATE, load_settings
from src.agents.analysis_agent import AnalysisAgent
from src.agents.creation_agent import CreationAgent
from src.agents.quality_agent import QualityAgent
from src.agents.rewrite_agent import RewriteAgent
from src.crawler.mock_crawler import MockCrawler
from src.crawler.xhs_crawler import XHSCrawler
from src.exporters.csv_exporter import export_results_to_csv
from src.processor.cleaner import clean_notes
from src.utils.logger import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XHS AI Agent content pipeline demo")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock", help="Crawler mode")
    parser.add_argument("--keyword", default="护肤", help="Keyword for live crawler interface")
    parser.add_argument("--limit", type=int, default=5, help="Max notes to process")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for output files")
    parser.add_argument(
        "--llm-mode",
        choices=["mock", "auto"],
        default="mock",
        help="mock: never call remote LLM; auto: use .env when API key exists",
    )
    parser.add_argument(
        "--storage-state",
        default=str(DEFAULT_STORAGE_STATE),
        help="Playwright storage state path for live crawler",
    )
    parser.add_argument("--headed", action="store_true", help="Run live crawler with a visible browser")
    return parser.parse_args()


def load_raw_notes(mode: str, keyword: str, limit: int, storage_state: str, headed: bool) -> list[dict]:
    if mode == "mock":
        return MockCrawler().fetch_notes(limit=limit)
    return XHSCrawler(storage_state_path=Path(storage_state), headless=not headed).fetch_notes(
        keyword=keyword,
        limit=limit,
    )


def run_pipeline(args: argparse.Namespace) -> tuple[Path, Path]:
    settings = load_settings(force_mock_llm=args.llm_mode == "mock")
    logger.info("LLM mode: %s", "mock" if settings.mock_llm else settings.openai_model)

    raw_notes = load_raw_notes(args.mode, args.keyword, args.limit, args.storage_state, args.headed)
    notes = clean_notes(raw_notes)
    logger.info("Loaded %s notes, %s notes after cleaning", len(raw_notes), len(notes))

    analysis_agent = AnalysisAgent(settings)
    rewrite_agent = RewriteAgent(settings)
    creation_agent = CreationAgent(settings)
    quality_agent = QualityAgent()

    results: list[dict] = []
    for index, note in enumerate(notes, start=1):
        logger.info("Processing note %s/%s: %s", index, len(notes), note["title"])
        analysis = analysis_agent.analyze(note)
        rewrite_strategy = rewrite_agent.create_strategy(note, analysis)
        creation = creation_agent.create_content(note, analysis, rewrite_strategy)
        quality = quality_agent.check(creation)
        results.append(
            {
                "original_note": note,
                "analysis": analysis,
                "rewrite_strategy": rewrite_strategy,
                "creation": creation,
                "quality_check": quality,
            }
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"pipeline_results_{timestamp}.json"
    csv_path = output_dir / f"pipeline_results_{timestamp}.csv"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    export_results_to_csv(results, csv_path)

    logger.info("JSON output: %s", json_path)
    logger.info("CSV output: %s", csv_path)
    return json_path, csv_path


def main() -> None:
    args = parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
