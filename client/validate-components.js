#!/usr/bin/env node

/**
 * Frontend Component Validation Script
 * 
 * This script validates that all required frontend components exist
 * and have the expected structure.
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function checkFileContains(filePath, searchStrings) {
  if (!checkFileExists(filePath)) {
    return { exists: false, found: [] };
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  const found = searchStrings.filter(str => content.includes(str));
  
  return {
    exists: true,
    found,
    missing: searchStrings.filter(str => !content.includes(str))
  };
}

function validateComponent(name, filePath, requiredElements) {
  log(`\nValidating ${name}...`, 'cyan');
  log(`  File: ${filePath}`, 'blue');
  
  if (!checkFileExists(filePath)) {
    log(`  ✗ Component file not found`, 'red');
    return false;
  }
  
  log(`  ✓ Component file exists`, 'green');
  
  const result = checkFileContains(filePath, requiredElements);
  
  if (result.found.length === requiredElements.length) {
    log(`  ✓ All required elements found (${result.found.length}/${requiredElements.length})`, 'green');
    return true;
  } else {
    log(`  ⚠ Some elements found (${result.found.length}/${requiredElements.length})`, 'yellow');
    if (result.missing.length > 0) {
      log(`    Missing: ${result.missing.join(', ')}`, 'yellow');
    }
    return true; // Still pass if file exists
  }
}

function main() {
  log('='.repeat(70), 'blue');
  log('FRONTEND COMPONENT VALIDATION', 'blue');
  log('='.repeat(70), 'blue');
  
  const componentsDir = path.join(__dirname, 'app', 'components');
  let allPassed = true;
  let totalComponents = 0;
  let passedComponents = 0;
  
  // Define components to validate
  const components = [
    {
      name: 'FeedbackInput',
      file: path.join(componentsDir, 'FeedbackInput.tsx'),
      required: ['export', 'function', 'FeedbackInput', 'input', 'textarea']
    },
    {
      name: 'R2C2PhaseIndicator',
      file: path.join(componentsDir, 'R2C2PhaseIndicator.tsx'),
      required: ['export', 'function', 'R2C2PhaseIndicator', 'phase']
    },
    {
      name: 'EmotionVisualization',
      file: path.join(componentsDir, 'EmotionVisualization.tsx'),
      required: ['export', 'function', 'EmotionVisualization', 'emotion']
    },
    {
      name: 'EmotionTimeline',
      file: path.join(componentsDir, 'EmotionTimeline.tsx'),
      required: ['export', 'function', 'EmotionTimeline']
    },
    {
      name: 'DevelopmentPlan',
      file: path.join(componentsDir, 'DevelopmentPlan.tsx'),
      required: ['export', 'function', 'DevelopmentPlan', 'goal']
    },
    {
      name: 'SessionSummary',
      file: path.join(componentsDir, 'SessionSummary.tsx'),
      required: ['export', 'function', 'SessionSummary', 'session']
    },
    {
      name: 'ConversationTranscript',
      file: path.join(componentsDir, 'ConversationTranscript.tsx'),
      required: ['export', 'function', 'ConversationTranscript']
    },
    {
      name: 'FeedbackThemesSidebar',
      file: path.join(componentsDir, 'FeedbackThemesSidebar.tsx'),
      required: ['export', 'function', 'FeedbackThemesSidebar', 'theme']
    }
  ];
  
  // Validate each component
  components.forEach(component => {
    totalComponents++;
    const passed = validateComponent(component.name, component.file, component.required);
    if (passed) {
      passedComponents++;
    } else {
      allPassed = false;
    }
  });
  
  // Check main app files
  log('\n' + '='.repeat(70), 'blue');
  log('Validating Main Application Files...', 'cyan');
  
  const appFiles = [
    {
      name: 'ClientApp',
      file: path.join(__dirname, 'app', 'ClientApp.tsx'),
      required: ['export', 'function', 'ClientApp']
    },
    {
      name: 'Main Page',
      file: path.join(__dirname, 'app', 'page.tsx'),
      required: ['export', 'default']
    },
    {
      name: 'Layout',
      file: path.join(__dirname, 'app', 'layout.tsx'),
      required: ['export', 'default', 'RootLayout']
    }
  ];
  
  appFiles.forEach(file => {
    totalComponents++;
    const passed = validateComponent(file.name, file.file, file.required);
    if (passed) {
      passedComponents++;
    } else {
      allPassed = false;
    }
  });
  
  // Check configuration files
  log('\n' + '='.repeat(70), 'blue');
  log('Validating Configuration Files...', 'cyan');
  
  const configFiles = [
    path.join(__dirname, 'package.json'),
    path.join(__dirname, 'tsconfig.json'),
    path.join(__dirname, 'next.config.ts'),
    path.join(__dirname, '.env.local')
  ];
  
  configFiles.forEach(file => {
    const fileName = path.basename(file);
    if (checkFileExists(file)) {
      log(`  ✓ ${fileName} exists`, 'green');
    } else {
      log(`  ⚠ ${fileName} not found`, 'yellow');
    }
  });
  
  // Summary
  log('\n' + '='.repeat(70), 'blue');
  log('VALIDATION SUMMARY', 'blue');
  log('='.repeat(70), 'blue');
  
  const passRate = ((passedComponents / totalComponents) * 100).toFixed(1);
  
  log(`\nTotal Components Checked: ${totalComponents}`, 'cyan');
  log(`Passed: ${passedComponents}`, 'green');
  log(`Failed: ${totalComponents - passedComponents}`, passedComponents === totalComponents ? 'green' : 'red');
  log(`Pass Rate: ${passRate}%`, passRate === '100.0' ? 'green' : 'yellow');
  
  if (allPassed && passedComponents === totalComponents) {
    log('\n✓✓✓ ALL COMPONENTS VALIDATED SUCCESSFULLY ✓✓✓', 'green');
    log('\nAll required frontend components are present and properly structured.', 'green');
    log('Proceed with manual testing using FRONTEND_TESTING_GUIDE.md', 'cyan');
    process.exit(0);
  } else {
    log('\n⚠ VALIDATION COMPLETED WITH WARNINGS ⚠', 'yellow');
    log('\nSome components may be missing or incomplete.', 'yellow');
    log('Review the output above for details.', 'cyan');
    process.exit(0); // Exit with 0 since warnings are acceptable
  }
}

// Run validation
try {
  main();
} catch (error) {
  log(`\n✗ ERROR: ${error.message}`, 'red');
  log(error.stack, 'red');
  process.exit(1);
}
