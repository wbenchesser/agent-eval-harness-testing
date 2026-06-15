"""Tests for dataset loader."""

from meta_evaluator.dataset.loader import parse_ground_truth


def test_parse_ground_truth_basic():
    """Test parsing basic CSV format."""
    csv_text = """# test name, category, real vulnerability, cwe, Benchmark version: 1.2, 2016-06-1
BenchmarkTest00001,pathtraver,true,22
BenchmarkTest00002,pathtraver,true,22
BenchmarkTest00003,hash,false,328"""

    results = parse_ground_truth(csv_text)

    assert len(results) == 3
    assert results[0]["test_name"] == "BenchmarkTest00001"
    assert results[0]["category"] == "pathtraver"
    assert results[0]["is_vulnerable"] is True
    assert results[0]["cwe"] == 22

    assert results[2]["is_vulnerable"] is False


def test_parse_ground_truth_skips_comments():
    """Test that comment lines are skipped."""
    csv_text = """# header comment
# another comment
BenchmarkTest00001,pathtraver,true,22"""

    results = parse_ground_truth(csv_text)

    assert len(results) == 1


def test_parse_ground_truth_handles_false():
    """Test parsing 'false' vulnerability flag."""
    csv_text = "BenchmarkTest00001,hash,false,328"

    results = parse_ground_truth(csv_text)

    assert results[0]["is_vulnerable"] is False


def test_parse_ground_truth_empty():
    """Test parsing empty CSV."""
    results = parse_ground_truth("")
    assert len(results) == 0
