#!/bin/bash

# R2C2 Voice Coach - Comprehensive Test Runner
# This script runs all tests for the R2C2 Voice Coach system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}R2C2 VOICE COACH - COMPREHENSIVE TEST SUITE${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Track test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    local test_dir=$3
    
    echo -e "${CYAN}Running: ${test_name}${NC}"
    echo -e "${YELLOW}Command: ${test_command}${NC}"
    echo ""
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ -n "$test_dir" ]; then
        cd "$test_dir"
    fi
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ ${test_name} PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo ""
        return 0
    else
        echo -e "${RED}✗ ${test_name} FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo ""
        return 1
    fi
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Backend Tests
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}BACKEND TESTS${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

run_test "Phase Transitions Test" \
    ".venv/bin/python test_phase_transitions.py" \
    "$SCRIPT_DIR/server"

cd "$SCRIPT_DIR"

run_test "Emotion Detection Test" \
    ".venv/bin/python test_emotion_detection.py" \
    "$SCRIPT_DIR/server"

cd "$SCRIPT_DIR"

run_test "Database Operations Test" \
    ".venv/bin/python test_database_comprehensive.py" \
    "$SCRIPT_DIR/server"

cd "$SCRIPT_DIR"

run_test "End-to-End Integration Test" \
    ".venv/bin/python test_end_to_end.py" \
    "$SCRIPT_DIR/server"

cd "$SCRIPT_DIR"

# Frontend Tests
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}FRONTEND TESTS${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

run_test "Frontend Component Validation" \
    "node validate-components.js" \
    "$SCRIPT_DIR/client"

cd "$SCRIPT_DIR"

# Summary
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

echo -e "Total Tests Run: ${CYAN}${TOTAL_TESTS}${NC}"
echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    PASS_RATE=100
else
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo -e "Pass Rate: ${CYAN}${PASS_RATE}%${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}======================================================================${NC}"
    echo -e "${GREEN}✓✓✓ ALL TESTS PASSED ✓✓✓${NC}"
    echo -e "${GREEN}======================================================================${NC}"
    echo ""
    echo -e "${GREEN}The R2C2 Voice Coach system has passed all tests!${NC}"
    echo -e "${CYAN}System is ready for deployment.${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}======================================================================${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED ✗${NC}"
    echo -e "${RED}======================================================================${NC}"
    echo ""
    echo -e "${RED}${FAILED_TESTS} test(s) failed. Please review the output above.${NC}"
    echo ""
    exit 1
fi
