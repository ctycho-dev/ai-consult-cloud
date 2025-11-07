# app/infrastructure/file_converter/llamaparse_converter.py
from __future__ import annotations
import time
from pathlib import Path
import tempfile
from typing import Tuple, Optional
from llama_parse import LlamaParse


class LlamaParseConverter:
    SUPPORTED_EXTS = {".xlsx", ".xls", ".xlsm"}

    def __init__(
        self,
        api_key: str,
        *,
        language: str = "en",
        verbose: bool = False,
        output_tables_as_HTML: bool = True,
        spreadsheet_extract_sub_tables: bool = True,
        spreadsheet_force_formula_computation: bool = True,
        max_retries: int = 2,
        backoff_base_sec: float = 1.5,
        tmp_dir: Optional[Path] = None,
    ) -> None:
        if not api_key:
            raise ValueError("LlamaParse: api_key is required")
        self.api_key = api_key
        self.language = language
        self.verbose = verbose
        self.output_tables_as_HTML = output_tables_as_HTML
        self.spreadsheet_extract_sub_tables = spreadsheet_extract_sub_tables
        self.spreadsheet_force_formula_computation = spreadsheet_force_formula_computation
        self.max_retries = max_retries
        self.backoff_base_sec = backoff_base_sec
        self.tmp_dir = Path(tmp_dir) if tmp_dir else Path(tempfile.gettempdir())

    def __call__(self, source_path: Path, filename: str) -> Tuple[Path, str]:
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_EXTS:
            return source_path, filename
        if not source_path.exists():
            raise FileNotFoundError(f"Excel source not found: {source_path}")

        stem = Path(filename).stem
        # ✅ create a unique temp file under system temp
        tmp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".md",
            prefix="conv_",
            dir=str(self.tmp_dir),
        )
        out_path = Path(tmp_file.name)
        new_filename = f"{stem}.md"

        parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            verbose=self.verbose,
            language=self.language,
            output_tables_as_HTML=self.output_tables_as_HTML,
            spreadsheet_extract_sub_tables=self.spreadsheet_extract_sub_tables,
            spreadsheet_force_formula_computation=self.spreadsheet_force_formula_computation,
        )

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                documents = parser.load_data(str(source_path))
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8", newline="\n") as f:
                    first = True
                    for doc in documents:
                        chunk = (getattr(doc, "text", "") or "").rstrip()
                        if not chunk:
                            continue
                        if not first:
                            f.write("\n\n")
                        f.write(chunk)
                        first = False
                    f.write("\n")
                return out_path, new_filename
            except Exception as e:
                last_err = e
                msg = str(e).lower()
                if "401" in msg or "403" in msg or "invalid api key" in msg:
                    # auth errors: fail fast; fallback logic will handle if configured
                    raise PermissionError(f"LlamaParse auth failed: {e}") from e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_base_sec * (2 ** attempt))
                else:
                    break

        assert last_err is not None
        raise RuntimeError(f"LlamaParse conversion failed: {last_err}") from last_err
