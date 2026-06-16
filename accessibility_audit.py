# accessibility_audit.py — Accessibility audit tool for text & braille validation

from typing import List, Dict, Tuple
from enum import Enum

class IssueSeverity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

class AccessibilityIssue:
    """Represents a single accessibility issue."""
    
    def __init__(self, severity: IssueSeverity, category: str, 
                 message: str, suggestion: str = "", position: int = -1):
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion
        self.position = position
    
    def to_dict(self) -> dict:
        return {
            'severity': self.severity.name,
            'category': self.category,
            'message': self.message,
            'suggestion': self.suggestion,
            'position': self.position,
        }

class AccessibilityAudit:
    """Main accessibility auditor for text and Braille."""
    
    def __init__(self):
        self.issues: List[AccessibilityIssue] = []
    
    def audit_text(self, text: str) -> Dict:
        """
        Audit text for accessibility issues.
        Returns {'issues': [...], 'status': ..., 'accessibility_score': ...}
        """
        self.issues = []
        
        if not text:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Content",
                "No text provided for audit",
                "Add text to analyze"
            ))
            result = self._get_summary()
            result['issues'] = self.issues
            return result
        
        # Check text length
        self._check_text_length(text)
        
        # Check character diversity
        self._check_character_set(text)
        
        # Check formatting
        self._check_formatting(text)
        
        # Check for problematic patterns
        self._check_problematic_patterns(text)
        
        # Check for special characters
        self._check_special_characters(text)
        
        result = self._get_summary()
        result['issues'] = self.issues
        return result
    
    def audit_braille_conversion(self, original_text: str, braille_text: str) -> Dict:
        """
        Audit a braille conversion for quality.
        Returns {'issues': [...], 'status': ..., 'accessibility_score': ...}
        """
        self.issues = []
        
        # Check for blank conversions
        if not braille_text and original_text:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.ERROR, "Conversion",
                "Braille conversion resulted in empty text",
                "Check if all characters are supported"
            ))
        
        # Check character mapping
        self._check_character_mapping(original_text, braille_text)
        
        # Check for lost information
        self._check_information_loss(original_text, braille_text)
        
        # Check for unmapped characters
        self._check_unmapped_characters(original_text, braille_text)
        
        result = self._get_summary()
        result['issues'] = self.issues
        return result
    
    def _check_text_length(self, text: str):
        """Check if text length is reasonable."""
        if len(text) > 10000:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Performance",
                f"Very long text ({len(text)} characters)",
                "Consider splitting into smaller chunks for better performance"
            ))
        elif len(text) < 5:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.INFO, "Content",
                "Very short text provided",
                "More content allows better analysis"
            ))
    
    def _check_character_set(self, text: str):
        """Check for character set diversity and support."""
        has_uppercase = any(c.isupper() for c in text)
        has_lowercase = any(c.islower() for c in text)
        has_numbers = any(c.isdigit() for c in text)
        has_special = any(not c.isalnum() and not c.isspace() for c in text)
        
        if not has_uppercase and not has_numbers and not has_special:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.INFO, "Content",
                "Text only contains lowercase letters",
                "Consider adding variety for better braille representation"
            ))
    
    def _check_formatting(self, text: str):
        """Check text formatting."""
        line_count = text.count('\n')
        
        if line_count > 50:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Formatting",
                f"Many line breaks ({line_count})",
                "Large number of lines may affect readability"
            ))
        
        # Check for excessive whitespace
        if '  ' in text:  # Double space
            self.issues.append(AccessibilityIssue(
                IssueSeverity.INFO, "Formatting",
                "Multiple consecutive spaces detected",
                "Consider normalizing whitespace for consistency"
            ))
    
    def _check_problematic_patterns(self, text: str):
        """Check for patterns that might cause issues."""
        # Check for repeated characters
        for i in range(len(text) - 3):
            if text[i] == text[i+1] == text[i+2] == text[i+3]:
                self.issues.append(AccessibilityIssue(
                    IssueSeverity.WARNING, "Pattern",
                    f"Long sequence of repeated character '{text[i]}' at position {i}",
                    "Repeated characters may confuse users",
                    i
                ))
                break  # Only report once
    
    def _check_special_characters(self, text: str):
        """Check for special or unusual characters."""
        special_chars = set()
        for char in text:
            if not char.isalnum() and not char.isspace() and ord(char) < 256:
                special_chars.add(char)
        
        if len(special_chars) > 10:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.INFO, "Content",
                f"Many special characters ({len(special_chars)} unique)",
                "Check that all special characters have proper braille mappings"
            ))
    
    def _check_character_mapping(self, original: str, braille: str):
        """Check if character mapping is reasonable."""
        # Simple heuristic: braille usually expands text slightly
        ratio = len(braille) / len(original) if original else 0
        
        if ratio < 0.5:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Conversion",
                "Braille text is significantly shorter than original",
                "Some characters may not have been converted properly"
            ))
        elif ratio > 3:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.INFO, "Conversion",
                "Braille text is much longer than original",
                "This is normal for some languages"
            ))
    
    def _check_information_loss(self, original: str, braille: str):
        """Check if information was lost in conversion."""
        # Check for unsupported characters (often converted to space or ?)
        if '?' in braille:
            count = braille.count('?')
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Conversion",
                f"Unrecognized characters ({count}) converted to '?'",
                "Some characters don't have braille mappings"
            ))
    
    def _check_unmapped_characters(self, original: str, braille: str):
        """Check for unmapped characters."""
        from braille_engine import text_to_braille
        from braille_maps import ENGLISH_TO_BRAILLE
        
        unmapped = set()
        for char in original:
            if char not in ENGLISH_TO_BRAILLE and char not in ' \n':
                unmapped.add(char)
        
        if unmapped:
            self.issues.append(AccessibilityIssue(
                IssueSeverity.WARNING, "Support",
                f"Found {len(unmapped)} unmapped character(s): {', '.join(list(unmapped)[:5])}",
                "These characters may not convert correctly to braille"
            ))
    
    def _get_summary(self) -> Dict:
        """Get summary statistics of issues."""
        severity_count = {
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
        }
        
        category_count = {}
        
        for issue in self.issues:
            severity_count[issue.severity.name] += 1
            category_count[issue.category] = category_count.get(issue.category, 0) + 1
        
        # Determine overall status
        if severity_count['ERROR'] > 0:
            status = '❌ Failed'
        elif severity_count['WARNING'] > 0:
            status = '⚠️ Warnings'
        else:
            status = '✅ Passed'
        
        return {
            'status': status,
            'total_issues': len(self.issues),
            'by_severity': severity_count,
            'by_category': category_count,
            'accessibility_score': max(0, 100 - len(self.issues) * 5),  # Simple scoring
        }
    
    def generate_report(self) -> str:
        """Generate a human-readable accessibility report."""
        report = []
        report.append("=" * 50)
        report.append("ACCESSIBILITY AUDIT REPORT")
        report.append("=" * 50)
        
        if not self.issues:
            report.append("\n✅ No accessibility issues found!\n")
        else:
            # Group by severity
            by_severity = {}
            for issue in self.issues:
                sev = issue.severity.name
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(issue)
            
            # Report each severity level
            for severity in ['ERROR', 'WARNING', 'INFO']:
                if severity in by_severity:
                    report.append(f"\n{severity}S ({len(by_severity[severity])}):")
                    report.append("-" * 30)
                    
                    for issue in by_severity[severity]:
                        report.append(f"• [{issue.category}] {issue.message}")
                        if issue.suggestion:
                            report.append(f"  → {issue.suggestion}")
        
        report.append("\n" + "=" * 50)
        return '\n'.join(report)

# Global instance
auditor = AccessibilityAudit()
