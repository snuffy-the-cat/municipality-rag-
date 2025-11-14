"""
Structured Logging Configuration
Provides JSON and text logging for indexing pipeline
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional


class StructuredLogger:
    """
    Structured logger for indexing pipeline
    Outputs both human-readable logs and structured JSON logs
    """

    def __init__(self, log_dir: Path, run_id: Optional[str] = None):
        """
        Initialize structured logger

        Args:
            log_dir: Directory to store log files
            run_id: Optional run identifier (defaults to timestamp)
        """

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate run ID if not provided
        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Log file paths
        self.json_log_path = self.log_dir / f"indexing_{self.run_id}.jsonl"
        self.text_log_path = self.log_dir / f"indexing_{self.run_id}.log"

        # Configure loguru for console and text file
        logger.remove()  # Remove default handler

        # Console output (human-readable)
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )

        # Text log file
        logger.add(
            self.text_log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="10 MB"
        )

        # Open JSON log file for structured logging
        self.json_log_file = open(self.json_log_path, 'a', encoding='utf-8')

        logger.info(f"Logging initialized - Run ID: {self.run_id}")
        logger.info(f"JSON log: {self.json_log_path}")
        logger.info(f"Text log: {self.text_log_path}")

    def log_structured(
        self,
        event_type: str,
        level: str,
        message: str,
        **kwargs
    ):
        """
        Log structured event to JSON log

        Args:
            event_type: Type of event (e.g., 'file_parsed', 'chunk_validated')
            level: Log level ('info', 'warning', 'error')
            message: Human-readable message
            **kwargs: Additional structured data
        """

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'run_id': self.run_id,
            'event_type': event_type,
            'level': level,
            'message': message,
            **kwargs
        }

        # Write to JSON log
        self.json_log_file.write(json.dumps(log_entry) + '\n')
        self.json_log_file.flush()

    def log_file_parsing(
        self,
        filename: str,
        parse_success: bool,
        parse_error: Optional[str] = None,
        metadata_fields: int = 0
    ):
        """Log file parsing event"""

        level = 'info' if parse_success else 'warning'

        self.log_structured(
            event_type='file_parsed',
            level=level,
            message=f"Parsed {filename}",
            filename=filename,
            parse_success=parse_success,
            parse_error=parse_error,
            metadata_fields=metadata_fields
        )

        if parse_success:
            logger.info(f"[OK] Parsed: {filename} ({metadata_fields} metadata fields)")
        else:
            logger.warning(f"[WARNING] Parsed with issues: {filename} - {parse_error}")

    def log_chunk_validation(
        self,
        filename: str,
        chunk_index: int,
        header: str,
        is_valid: bool,
        severity: str,
        issues: list,
        metadata: Dict[str, Any]
    ):
        """Log chunk validation event"""

        self.log_structured(
            event_type='chunk_validated',
            level=severity,
            message=f"Chunk {chunk_index} in {filename}",
            filename=filename,
            chunk_index=chunk_index,
            header=header,
            is_valid=is_valid,
            severity=severity,
            issues=issues,
            category=metadata.get('category'),
            title=metadata.get('title')
        )

        if severity == 'critical':
            logger.error(f"[CRITICAL] {filename} chunk {chunk_index}: {', '.join(issues)}")
        elif severity == 'warning':
            logger.debug(f"[WARNING] {filename} chunk {chunk_index}: {', '.join(issues)}")

    def log_chunk_indexed(
        self,
        filename: str,
        chunk_index: int,
        chunk_id: str
    ):
        """Log successful chunk indexing"""

        self.log_structured(
            event_type='chunk_indexed',
            level='info',
            message=f"Indexed chunk {chunk_index} from {filename}",
            filename=filename,
            chunk_index=chunk_index,
            chunk_id=chunk_id
        )

    def log_summary(
        self,
        total_files: int,
        total_chunks: int,
        indexed_chunks: int,
        warnings: int,
        errors: int
    ):
        """Log indexing summary"""

        self.log_structured(
            event_type='indexing_summary',
            level='info',
            message='Indexing completed',
            total_files=total_files,
            total_chunks=total_chunks,
            indexed_chunks=indexed_chunks,
            warnings=warnings,
            errors=errors
        )

        logger.info("="*80)
        logger.info("INDEXING SUMMARY")
        logger.info("="*80)
        logger.info(f"Total files: {total_files}")
        logger.info(f"Total chunks: {total_chunks}")
        logger.info(f"Indexed chunks: {indexed_chunks}")
        logger.info(f"Warnings: {warnings}")
        logger.info(f"Errors: {errors}")

    def close(self):
        """Close log files"""
        if hasattr(self, 'json_log_file'):
            self.json_log_file.close()


def main():
    """Test the structured logger"""
    import tempfile

    # Create temp log directory
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs"

        # Initialize logger
        structured_logger = StructuredLogger(log_dir, run_id="test_run")

        # Test different log types
        structured_logger.log_file_parsing(
            filename="test_file.md",
            parse_success=True,
            metadata_fields=5
        )

        structured_logger.log_file_parsing(
            filename="bad_file.md",
            parse_success=False,
            parse_error="YAML parsing failed",
            metadata_fields=0
        )

        structured_logger.log_chunk_validation(
            filename="test_file.md",
            chunk_index=0,
            header="# Overview",
            is_valid=True,
            severity='warning',
            issues=['YAML parsing failed'],
            metadata={'title': 'Test Doc', 'category': 'Unknown'}
        )

        structured_logger.log_chunk_indexed(
            filename="test_file.md",
            chunk_index=0,
            chunk_id="test_file_chunk_0"
        )

        structured_logger.log_summary(
            total_files=2,
            total_chunks=5,
            indexed_chunks=5,
            warnings=1,
            errors=0
        )

        structured_logger.close()

        # Show JSON log contents
        print("\n" + "="*80)
        print("JSON LOG CONTENTS:")
        print("="*80)

        json_log = log_dir / "indexing_test_run.jsonl"
        with open(json_log, 'r') as f:
            for line in f:
                data = json.loads(line)
                print(json.dumps(data, indent=2))
                print()


if __name__ == "__main__":
    main()
