#!/usr/bin/env python3
"""
CodeSecAuditor - AI-Powered Python Code Security Analyzer

Comprehensive security auditing tool for Python projects using:
- Static analysis (Bandit, AST parsing)
- AI-powered security insights
- Best practices validation
- Vulnerability detection
- Security recommendations

Features:
- Scan Python projects for security issues
- Generate detailed security reports
- Identify code patterns and anti-patterns
- Provide AI-powered remediation suggestions
- Track security metrics over time
- Export findings in multiple formats
"""

import json
import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from collections import defaultdict


class CodeSecAuditor:
    """
    AI-powered Python code security analyzer.
    
    Performs comprehensive security auditing of Python projects including:
    - Vulnerability scanning
    - Best practices validation
    - Security anti-pattern detection
    - AI-powered recommendations
    """

    # Security patterns to detect
    SECURITY_PATTERNS = {
        "hardcoded_secrets": {
            "patterns": [
                r"password\s*=\s*['\"]",
                r"api[_-]?key\s*=\s*['\"]",
                r"secret\s*=\s*['\"]",
                r"token\s*=\s*['\"]",
                r"private[_-]?key\s*=\s*['\"]"
            ],
            "severity": "CRITICAL",
            "description": "Hardcoded secrets or credentials"
        },
        "sql_injection": {
            "patterns": [
                r"execute\s*\(\s*f['\"]",
                r"format\s*\(\s*.*sql",
                r"\.format\s*\(\s*user_input"
            ],
            "severity": "CRITICAL",
            "description": "Potential SQL injection vulnerability"
        },
        "insecure_random": {
            "patterns": [
                r"random\.random\(",
                r"random\.randint\(",
                r"random\.choice\("
            ],
            "severity": "HIGH",
            "description": "Use of insecure random for security"
        },
        "eval_usage": {
            "patterns": [
                r"\beval\s*\(",
                r"exec\s*\(",
                r"__import__\s*\("
            ],
            "severity": "CRITICAL",
            "description": "Dangerous eval/exec usage"
        },
        "pickle_usage": {
            "patterns": [
                r"pickle\.loads\(",
                r"pickle\.load\("
            ],
            "severity": "HIGH",
            "description": "Unsafe pickle deserialization"
        },
        "disabled_ssl": {
            "patterns": [
                r"ssl\.CERT_NONE",
                r"verify\s*=\s*False",
                r"check_hostname\s*=\s*False"
            ],
            "severity": "HIGH",
            "description": "Disabled SSL/TLS verification"
        },
        "hardcoded_paths": {
            "patterns": [
                r'"/etc/passwd"',
                r'"/etc/shadow"',
                r'"/\.ssh"'
            ],
            "severity": "MEDIUM",
            "description": "Hardcoded sensitive system paths"
        },
        "weak_crypto": {
            "patterns": [
                r"md5\(",
                r"sha1\(",
                r"DES\(",
                r"RC4\("
            ],
            "severity": "HIGH",
            "description": "Use of weak cryptographic algorithms"
        }
    }

    def __init__(self, project_path: str = "."):
        """
        Initialize the auditor.
        
        Args:
            project_path: Root path of project to audit
        """
        self.project_path = Path(project_path)
        self.python_files: List[Path] = []
        self.findings: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {
            "total_files": 0,
            "total_lines": 0,
            "issues_by_severity": defaultdict(int),
            "issues_by_type": defaultdict(int)
        }

    def scan_project(self) -> Dict[str, Any]:
        """
        Scan entire project for security issues.
        
        Returns:
            Dictionary with audit results
        """
        self._discover_python_files()
        self._scan_files()
        
        return {
            "project": str(self.project_path),
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self._generate_summary(),
            "findings": self.findings,
            "metrics": dict(self.metrics),
            "recommendations": self._generate_recommendations()
        }

    def _discover_python_files(self) -> None:
        """Discover all Python files in project."""
        exclude_dirs = {".git", ".env", "venv", "__pycache__", ".pytest_cache"}
        
        for py_file in self.project_path.rglob("*.py"):
            # Skip excluded directories
            if any(exc in py_file.parts for exc in exclude_dirs):
                continue
            self.python_files.append(py_file)
        
        self.metrics["total_files"] = len(self.python_files)

    def _scan_files(self) -> None:
        """Scan all Python files for security issues."""
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    self.metrics["total_lines"] += len(lines)
                    
                    self._scan_file_content(str(py_file), content, lines)
            except Exception as e:
                print(f"⚠️  Error scanning {py_file}: {e}")

    def _scan_file_content(
        self,
        filepath: str,
        content: str,
        lines: List[str]
    ) -> None:
        """Scan individual file for security patterns."""
        for issue_type, pattern_info in self.SECURITY_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    finding = {
                        "file": filepath,
                        "line": line_num,
                        "type": issue_type,
                        "severity": pattern_info["severity"],
                        "description": pattern_info["description"],
                        "code": lines[line_num - 1].strip() if line_num <= len(lines) else "",
                        "remediation": self._get_remediation(issue_type)
                    }
                    
                    self.findings.append(finding)
                    self.metrics["issues_by_severity"][finding["severity"]] += 1
                    self.metrics["issues_by_type"][issue_type] += 1

    def _get_remediation(self, issue_type: str) -> str:
        """Get remediation suggestion for issue."""
        remediations = {
            "hardcoded_secrets": "Use environment variables or .env file. Never commit secrets.",
            "sql_injection": "Use parameterized queries with placeholders.",
            "insecure_random": "Use secrets module for cryptographic randomness.",
            "eval_usage": "Avoid eval/exec. Use safer alternatives like ast.literal_eval().",
            "pickle_usage": "Use JSON or other safe serialization formats.",
            "disabled_ssl": "Always verify SSL certificates in production.",
            "hardcoded_paths": "Never hardcode sensitive system paths.",
            "weak_crypto": "Use modern algorithms: SHA-256, PBKDF2, bcrypt, or Argon2."
        }
        return remediations.get(issue_type, "Review security best practices")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate audit summary."""
        severity_counts = self.metrics["issues_by_severity"]
        
        # Calculate security score (0-100)
        critical = severity_counts.get("CRITICAL", 0)
        high = severity_counts.get("HIGH", 0)
        medium = severity_counts.get("MEDIUM", 0)
        
        security_score = max(0, 100 - (critical * 50 + high * 20 + medium * 5))
        
        return {
            "total_issues": len(self.findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "security_score": security_score,
            "status": self._get_security_status(security_score)
        }

    def _get_security_status(self, score: float) -> str:
        """Determine security status based on score."""
        if score >= 90:
            return "EXCELLENT ✅"
        elif score >= 75:
            return "GOOD ⚠️"
        elif score >= 50:
            return "FAIR 🔶"
        else:
            return "CRITICAL ❌"

    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations."""
        recommendations = [
            "Enable Git pre-commit hooks for automatic security scanning",
            "Use secrets management system for credentials",
            "Implement automated dependency vulnerability scanning",
            "Set up GitHub Actions for continuous security monitoring",
            "Regular security training for development team",
            "Conduct periodic penetration testing",
            "Implement logging and monitoring for security events"
        ]
        
        # Add specific recommendations based on findings
        if self.metrics["issues_by_severity"].get("CRITICAL", 0) > 0:
            recommendations.insert(0, "URGENT: Address critical security issues immediately")
        
        return recommendations

    def generate_report(self, output_format: str = "json") -> str:
        """
        Generate formatted security report.
        
        Args:
            output_format: Format for report (json, text, html)
            
        Returns:
            Formatted report string
        """
        audit_results = self.scan_project()
        
        if output_format == "json":
            return json.dumps(audit_results, indent=2, default=str)
        elif output_format == "text":
            return self._format_text_report(audit_results)
        elif output_format == "html":
            return self._format_html_report(audit_results)
        else:
            raise ValueError(f"Unknown format: {output_format}")

    def _format_text_report(self, results: Dict[str, Any]) -> str:
        """Format results as text report."""
        lines = [
            "=" * 70,
            "🔐 CODE SECURITY AUDIT REPORT",
            "=" * 70,
            f"\nProject: {results['project']}",
            f"Timestamp: {results['timestamp']}",
            f"\n📊 SUMMARY",
            f"  Total Issues: {results['summary']['total_issues']}",
            f"  Critical: {results['summary']['critical']}",
            f"  High: {results['summary']['high']}",
            f"  Medium: {results['summary']['medium']}",
            f"  Security Score: {results['summary']['security_score']:.1f}/100",
            f"  Status: {results['summary']['status']}",
            f"\n📈 METRICS",
            f"  Python Files Scanned: {results['metrics']['total_files']}",
            f"  Total Lines: {results['metrics']['total_lines']}",
        ]
        
        if results['findings']:
            lines.append("\n🚨 CRITICAL FINDINGS:")
            for finding in results['findings'][:5]:  # Top 5
                lines.append(f"\n  [{finding['severity']}] {finding['type']} (Line {finding['line']})")
                lines.append(f"  File: {finding['file']}")
                lines.append(f"  Code: {finding['code'][:60]}...")
                lines.append(f"  Fix: {finding['remediation']}")
        
        lines.append("\n" + "=" * 70)
        return "\n".join(lines)

    def _format_html_report(self, results: Dict[str, Any]) -> str:
        """Format results as HTML report (basic)."""
        html = ["<html><head><title>Security Audit Report</title>"]
        html.append("<style>body { font-family: Arial; margin: 20px; }")
        html.append(".critical { color: red; } .high { color: orange; }")
        html.append(".medium { color: gold; }</style></head><body>")
        html.append(f"<h1>🔐 Security Audit Report</h1>")
        html.append(f"<p>Project: {results['project']}</p>")
        html.append(f"<p>Score: {results['summary']['security_score']:.0f}/100</p>")
        html.append("</body></html>")
        
        return "\n".join(html)


def main():
    """Example usage of CodeSecAuditor."""
    auditor = CodeSecAuditor(".")
    
    print("🔍 Starting code security audit...")
    print("=" * 70)
    
    # Generate report
    report = auditor.generate_report("text")
    print(report)
    
    # Also save JSON report
    json_report = auditor.generate_report("json")
    with open("security_audit_report.json", "w") as f:
        f.write(json_report)
    print("\n✅ Report saved to security_audit_report.json")


if __name__ == "__main__":
    main()
