"""Tests for logging functionality."""

import os
import tempfile


class TestLoggingUtils:
    """Tests for logging utility functions."""

    def test_get_cairo_time(self):
        """Test getting Cairo timezone time."""
        from app.providers import get_cairo_time
        cairo_time = get_cairo_time()
        assert cairo_time is not None
        assert cairo_time.tzinfo is not None

    def test_get_cairo_timestamp(self):
        """Test getting Cairo timestamp."""
        from app.providers import get_cairo_timestamp
        timestamp = get_cairo_timestamp()
        # Should match format YYYY-MM-DD_HH-MM-SS
        assert len(timestamp) == 19
        assert timestamp[4] == "-"
        assert timestamp[7] == "-"
        assert timestamp[10] == "_"

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from app.providers import sanitize_filename

        assert sanitize_filename("Normal Name") == "Normal_Name"
        assert sanitize_filename("With/Slash") == "With_Slash"
        assert sanitize_filename("Multiple   Spaces") == "Multiple_Spaces"
        assert sanitize_filename("Special!@#$%Chars") == "Special_Chars"
        assert sanitize_filename("___Leading") == "Leading"
        assert sanitize_filename("Trailing___") == "Trailing"

    def test_create_search_log(self):
        """Test creating a search log file."""
        from app.providers import create_search_log, _config

        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily override log directory
            original_config = _config.copy()
            _config["logging"] = {"log_dir": tmpdir}

            try:
                results = [
                    {"title": "Test Article", "link": "https://example.com", "published": "2026-01-20", "source": "Test"},
                ]
                log_path = create_search_log(
                    company_name="TestCompany",
                    results=results,
                    url="https://example.com/search",
                    query="test query"
                )

                # Check file was created
                assert os.path.exists(log_path)
                assert "TestCompany" in log_path
                assert log_path.endswith(".log")

                # Check file content
                with open(log_path, "r") as f:
                    content = f.read()
                    assert "TestCompany" in content
                    assert "test query" in content
                    assert "Test Article" in content
                    assert "Cairo Time" in content

            finally:
                # Restore config
                _config.clear()
                _config.update(original_config)

    def test_create_search_log_without_company(self):
        """Test creating a search log without company name."""
        from app.providers import create_search_log, _config

        with tempfile.TemporaryDirectory() as tmpdir:
            original_config = _config.copy()
            _config["logging"] = {"log_dir": tmpdir}

            try:
                log_path = create_search_log(
                    company_name=None,
                    results=[],
                    url="https://example.com",
                    query="test"
                )

                assert os.path.exists(log_path)
                assert "search_" in log_path

            finally:
                _config.clear()
                _config.update(original_config)
