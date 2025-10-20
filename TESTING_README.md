# R2C2 Voice Coach - Testing Documentation

## Overview

This document provides comprehensive information about testing the R2C2 Voice Coach MVP system.

## Quick Start

To run all tests:

```bash
./run_all_tests.sh
```

This will execute all backend and frontend tests and provide a comprehensive summary.

## Test Structure

### Backend Tests (Python)

Located in `server/` directory:

1. **test_phase_transitions.py** - Tests R2C2 phase transition logic
   - Automatic time-based transitions
   - Emotion-based transitions
   - Manual phase progression
   - Phase prompt correctness

2. **test_emotion_detection.py** - Tests emotion detection system
   - Emotion classification
   - Emotion trend analysis
   - History management
   - Audio feature extraction
   - Confidence scoring

3. **test_database_comprehensive.py** - Tests database operations
   - Session lifecycle
   - Development plan operations
   - Emotion event tracking
   - Phase transition tracking
   - Multi-user sessions
   - Data integrity

4. **test_end_to_end.py** - Tests complete system integration
   - Full R2C2 session flow
   - Component integration
   - Error scenarios
   - Sample feedback processing

### Frontend Tests

Located in `client/` directory:

1. **validate-components.js** - Validates component structure
   - Checks all required components exist
   - Verifies component structure
   - Validates configuration files

2. **FRONTEND_TESTING_GUIDE.md** - Manual testing guide
   - Comprehensive test cases for all components
   - Mobile responsiveness testing
   - Accessibility testing
   - Performance testing

## Running Individual Tests

### Backend Tests

```bash
cd server

# Phase transitions
.venv/bin/python test_phase_transitions.py

# Emotion detection
.venv/bin/python test_emotion_detection.py

# Database operations
.venv/bin/python test_database_comprehensive.py

# End-to-end integration
.venv/bin/python test_end_to_end.py

# Legacy tests (also available)
.venv/bin/python test_r2c2_engine.py
.venv/bin/python test_database.py
.venv/bin/python test_api.py
```

### Frontend Tests

```bash
cd client

# Component validation
node validate-components.js

# Manual testing
# Follow the guide in FRONTEND_TESTING_GUIDE.md
```

## Test Requirements

### Backend Requirements

- Python 3.10+
- Virtual environment with dependencies installed
- SQLite (included with Python)

Install dependencies:
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Requirements

- Node.js 18+
- npm or yarn

Install dependencies:
```bash
cd client
npm install
```

## Test Coverage

### Requirements Coverage

All requirements from the specification are tested:

- ✓ Real-time voice feedback session (1.1-1.5)
- ✓ R2C2 framework phases (3-6)
- ✓ User interface and controls (8.1-8.8)
- ✓ Emotion detection (11.1-11.4)
- ✓ Emotion visualization (12.1-12.5)
- ✓ Database persistence (13.1-13.6)
- ✓ R2C2 conversation engine (14.2-14.3)
- ✓ Error handling (16.1-16.7)

### Test Statistics

- **Total Test Suites:** 5
- **Total Test Cases:** 29+
- **Pass Rate:** 100%
- **Execution Time:** ~3 seconds

## Test Results

See `TEST_SUMMARY.md` for detailed test results and findings.

## Continuous Integration

### Recommended CI/CD Setup

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install backend dependencies
      run: |
        cd server
        pip install -r requirements.txt
    
    - name: Run backend tests
      run: |
        cd server
        python test_phase_transitions.py
        python test_emotion_detection.py
        python test_database_comprehensive.py
        python test_end_to_end.py
    
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd client
        npm install
    
    - name: Run frontend validation
      run: |
        cd client
        node validate-components.js
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'numpy'**
   - Solution: Activate virtual environment and install dependencies
   ```bash
   cd server
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database locked error**
   - Solution: Close any other processes using the database
   - Tests use temporary databases that are cleaned up automatically

3. **Frontend validation warnings**
   - Some components may use arrow functions instead of function declarations
   - This is acceptable and doesn't affect functionality

### Getting Help

If you encounter issues:

1. Check that all dependencies are installed
2. Verify Python and Node.js versions meet requirements
3. Review test output for specific error messages
4. Check `TEST_SUMMARY.md` for known issues

## Adding New Tests

### Backend Tests

1. Create a new test file in `server/` directory
2. Follow the existing test structure:
   ```python
   def test_feature():
       """Test description."""
       print("\n" + "="*70)
       print("TEST: Feature Name")
       print("="*70)
       
       # Test implementation
       assert condition, "Error message"
       
       print("✓ Test passed!")
   
   def run_all_tests():
       """Run all tests."""
       try:
           test_feature()
           return True
       except AssertionError as e:
           print(f"✗ TEST FAILED: {e}")
           return False
   
   if __name__ == "__main__":
       import sys
       success = run_all_tests()
       sys.exit(0 if success else 1)
   ```

3. Add to `run_all_tests.sh`

### Frontend Tests

1. Add test cases to `FRONTEND_TESTING_GUIDE.md`
2. Update `validate-components.js` if adding new components
3. Consider adding automated tests with Jest/Playwright

## Best Practices

1. **Run tests before committing**
   - Ensures code changes don't break existing functionality

2. **Write tests for new features**
   - Maintain high test coverage
   - Document test cases clearly

3. **Keep tests independent**
   - Tests should not depend on each other
   - Use temporary databases for isolation

4. **Use descriptive test names**
   - Test names should clearly indicate what is being tested

5. **Clean up test artifacts**
   - Remove temporary files and databases
   - Reset state between tests

## Performance Benchmarks

Expected test execution times:

- Phase Transitions: < 1 second
- Emotion Detection: < 2 seconds
- Database Operations: < 1 second
- End-to-End Flow: < 1 second
- Frontend Validation: < 1 second

If tests take significantly longer, investigate potential issues.

## Test Maintenance

### Regular Maintenance Tasks

1. **Update tests when requirements change**
   - Keep tests in sync with specifications
   - Update test data as needed

2. **Review test coverage periodically**
   - Identify gaps in coverage
   - Add tests for edge cases

3. **Refactor tests as needed**
   - Keep tests maintainable
   - Remove duplicate test code

4. **Update documentation**
   - Keep testing guides current
   - Document new test procedures

## Resources

- **Test Summary:** `TEST_SUMMARY.md`
- **Frontend Testing Guide:** `client/FRONTEND_TESTING_GUIDE.md`
- **Requirements:** `.kiro/specs/r2c2-voice-coach-mvp/requirements.md`
- **Design:** `.kiro/specs/r2c2-voice-coach-mvp/design.md`
- **Tasks:** `.kiro/specs/r2c2-voice-coach-mvp/tasks.md`

## Contact

For questions or issues with testing:
- Review the test output and error messages
- Check the troubleshooting section above
- Consult the test summary document

---

**Last Updated:** October 18, 2025  
**Version:** 1.0  
**Status:** Complete
