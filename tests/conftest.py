"""Pytest fixtures for testing."""

import pytest

from meta_evaluator.dataset.loader import TestCase
from meta_evaluator.judge.verdict import JudgeResult, Verdict


@pytest.fixture
def sample_test_case():
    """A single vulnerable test case (path traversal)."""
    return TestCase(
        test_name="BenchmarkTest00001",
        category="pathtraver",
        is_vulnerable=True,
        cwe=22,
        source_code="""
package org.owasp.benchmark.testcode;

import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class BenchmarkTest00001 extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        String param = request.getParameter("fileName");
        String fileName = "/tmp/" + param;
        try {
            FileInputStream fis = new FileInputStream(fileName);
        } catch (Exception e) {
            // handle exception
        }
    }
}
""",
    )


@pytest.fixture
def sample_clean_case():
    """A single clean test case (no vulnerability)."""
    return TestCase(
        test_name="BenchmarkTest00099",
        category="trustbound",
        is_vulnerable=False,
        cwe=501,
        source_code="""
package org.owasp.benchmark.testcode;

import javax.servlet.*;
import javax.servlet.http.*;

public class BenchmarkTest00099 extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        String param = request.getParameter("input");
        String bar = "safe_value";  // hardcoded safe value
        request.getSession().setAttribute("data", bar);
    }
}
""",
    )


@pytest.fixture
def sample_verdict_correct():
    """A correct verdict for a vulnerable case."""
    return Verdict(is_vulnerable=True, cwe=22, confidence=0.9, reasoning="Path traversal")


@pytest.fixture
def sample_verdict_incorrect():
    """An incorrect verdict (false negative)."""
    return Verdict(
        is_vulnerable=False, cwe=None, confidence=0.7, reasoning="Looks safe to me"
    )


@pytest.fixture
def sample_judge_result(sample_test_case, sample_verdict_correct):
    """A complete judge result."""
    return JudgeResult(
        test_name=sample_test_case.test_name,
        ground_truth_vulnerable=sample_test_case.is_vulnerable,
        ground_truth_cwe=sample_test_case.cwe,
        ground_truth_category=sample_test_case.category,
        verdict=sample_verdict_correct,
        input_tokens=1500,
        output_tokens=200,
        cost_usd=0.0125,
        latency_seconds=2.5,
        model="claude-opus-4-8",
    )
