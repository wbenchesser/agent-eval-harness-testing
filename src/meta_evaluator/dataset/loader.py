"""OWASP Benchmark ground truth and source code loading."""

import csv
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass(frozen=True)
class TestCase:
    """A single OWASP Benchmark test case with ground truth."""

    test_name: str  # "BenchmarkTest00001"
    category: str  # "pathtraver", "sqli", etc.
    is_vulnerable: bool  # ground truth
    cwe: int  # e.g. 22, 78, 89
    source_code: str  # full Java file content


def parse_ground_truth(csv_text: str) -> list[dict]:
    """Parse expectedresults CSV. Skips comment lines starting with '#'."""
    lines = [line for line in csv_text.strip().splitlines() if not line.startswith("#")]
    reader = csv.reader(lines)
    results = []

    for row in reader:
        if len(row) < 4:
            continue
        results.append(
            {
                "test_name": row[0].strip(),
                "category": row[1].strip(),
                "is_vulnerable": row[2].strip().lower() == "true",
                "cwe": int(row[3].strip()),
            }
        )

    return results


async def fetch_source_code(test_name: str, base_url: str, client: httpx.AsyncClient) -> str:
    """Fetch a single Java source file from GitHub."""
    url = f"{base_url}/{test_name}.java"
    resp = await client.get(url)
    resp.raise_for_status()
    return resp.text


def load_from_local(test_name: str, repo_path: Path) -> str:
    """Load source from a cloned BenchmarkJava repo."""
    file_path = (
        repo_path / "src/main/java/org/owasp/benchmark/testcode" / f"{test_name}.java"
    )
    if not file_path.exists():
        raise FileNotFoundError(f"Test case file not found: {file_path}")
    return file_path.read_text()


async def load_dataset(
    csv_url: str,
    source_base_url: str,
    local_repo_path: Path | None = None,
) -> list[TestCase]:
    """Full pipeline: fetch CSV, fetch source files, return TestCase list."""

    # 1. Fetch and parse CSV (ground truth)
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(csv_url)
        resp.raise_for_status()
        csv_text = resp.text

    ground_truth = parse_ground_truth(csv_text)
    print(f"Loaded {len(ground_truth)} test cases from CSV")

    # 2. For each entry, fetch source code (local or remote)
    cases = []

    if local_repo_path:
        print(f"Loading source files from local repo: {local_repo_path}")
        for entry in ground_truth:
            source_code = load_from_local(entry["test_name"], local_repo_path)
            cases.append(TestCase(**entry, source_code=source_code))
    else:
        print("Fetching source files from GitHub...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, entry in enumerate(ground_truth):
                if (i + 1) % 100 == 0:
                    print(f"  Fetched {i + 1}/{len(ground_truth)} files...")
                source_code = await fetch_source_code(
                    entry["test_name"], source_base_url, client
                )
                cases.append(TestCase(**entry, source_code=source_code))

    print(f"Loaded {len(cases)} test cases with source code")
    return cases
