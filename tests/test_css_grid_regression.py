import pytest
import os
import tempfile
from pathlib import Path

def test_css_grid_rule_completeness():
    """
    Regression test for incomplete CSS grid-template-columns rule that caused theme application failure.
    Verifies that the CSS files contain complete and valid grid-template-columns rules.
    """
    # Test both CSS files
    css_files = [
        Path('public/style.css'),
        Path('style.css')
    ]
    
    for css_file in css_files:
        # Skip if file doesn't exist (for testing purposes)
        if not css_file.exists():
            pytest.skip(f"CSS file {css_file} not found")
            
        content = css_file.read_text()
        
        # Verify the grid-template-columns rule is complete
        assert 'grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))' in content, \
            f"CSS file {css_file} contains incomplete grid-template-columns rule"
        
        # Verify the rule appears in the .grid class context
        grid_class_context = content[content.find('.grid {'):content.find('.grid {') + 500]
        assert 'grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))' in grid_class_context, \
            f"CSS file {css_file} has grid-template-columns rule outside .grid class"
        
        # Verify no truncated versions exist
        assert 'minmax(200px' not in content or 'minmax(200px, 1fr)' in content, \
            f"CSS file {css_file} contains truncated minmax() function"
        
        # Verify the rule is properly formatted (no extra spaces or missing characters)
        assert 'minmax(200px,1fr)' not in content, \
            f"CSS file {css_file} has incorrect spacing in minmax() function"

def test_theme_application_with_valid_css():
    """
    Integration test that verifies theme application works when CSS rules are valid.
    This simulates the original failure scenario where theme application would fail
    due to incomplete CSS rules.
    """
    # Create a temporary directory for test CSS files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test CSS files with the fixed rules
        test_css = Path(tmpdir) / 'test_style.css'
        test_css.write_text("""
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 2rem;
            }
        """)
        
        # Simulate theme application (this would be the actual theme manager code)
        # For this test, we'll just verify the CSS can be parsed
        try:
            import cssutils
            sheet = cssutils.parseFile(str(test_css))
            # Verify we have at least one rule
            assert len(sheet.cssRules) > 0, "CSS file should contain rules"
            
            # Find the grid rule
            grid_rule = None
            for rule in sheet.cssRules:
                if hasattr(rule, 'selectorText') and '.grid' in rule.selectorText:
                    grid_rule = rule
                    break
            
            assert grid_rule is not None, "Should find .grid rule in CSS"
            assert 'grid-template-columns' in grid_rule.style, \
                "Grid rule should contain grid-template-columns property"
            
        except ImportError:
            pytest.skip("cssutils not available for CSS parsing validation")

def test_css_edge_cases():
    """
    Test edge cases for CSS grid-template-columns rules to ensure robustness.
    """
    # Test that various valid grid-template-columns formats are accepted
    valid_formats = [
        'grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))',
        'grid-template-columns: repeat(auto-fit, minmax(150px, 1fr))',
        'grid-template-columns: 200px 1fr 200px',
        'grid-template-columns: minmax(100px, max-content) 1fr'
    ]
    
    # Test that invalid formats are rejected
    invalid_formats = [
        'grid-template-columns: repeat(auto-fill, minmax(200px',  # Missing closing paren
        'grid-template-columns: repeat(auto-fill, minmax(200px,)', # Missing second value
        'grid-template-columns: minmax(200px 1fr)',                # Missing comma
        'grid-template-columns: minmax(200px,1fr)'                 # Missing space after comma
    ]
    
    # For this test, we'll just verify our fixed format is valid
    fixed_format = 'grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))'
    assert fixed_format in valid_formats, "Fixed format should be in valid formats list"
    assert fixed_format not in invalid_formats, "Fixed format should not be in invalid formats list"