# Frontend Component Testing Guide

This guide provides comprehensive manual testing procedures for all R2C2 Voice Coach frontend components.

## Prerequisites

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Ensure the backend server is running:
   ```bash
   cd ../server
   .venv/bin/python -m api.server
   ```

## Component Testing Checklist

### 1. Feedback Input Component

**Location:** `app/components/FeedbackInput.tsx`

**Requirements:** 8.1, 12.1

**Test Cases:**

- [ ] **TC1.1: Text Input**
  - Navigate to the application
  - Verify feedback input form is visible
  - Enter sample feedback text
  - Verify text is accepted and displayed correctly
  - Test with various text lengths (short, medium, long)

- [ ] **TC1.2: File Upload**
  - Click file upload button
  - Select a CSV file with feedback data
  - Verify file is accepted
  - Verify feedback is parsed and displayed
  - Test with JSON file format
  - Test with invalid file format (should show error)

- [ ] **TC1.3: Validation**
  - Try to start session without feedback
  - Verify appropriate error message is shown
  - Enter valid feedback
  - Verify "Start Session" button becomes enabled

**Expected Results:**
- Feedback input accepts text and file uploads
- Validation prevents empty submissions
- Error messages are clear and helpful
- UI is responsive and intuitive

---

### 2. R2C2 Phase Indicator

**Location:** `app/components/R2C2PhaseIndicator.tsx`

**Requirements:** 8.3, 8.4

**Test Cases:**

- [ ] **TC2.1: Phase Display**
  - Start a coaching session
  - Verify current phase is displayed prominently
  - Verify phase name is clear (Relationship, Reaction, Content, Coaching)
  - Check that phase description is shown

- [ ] **TC2.2: Phase Transitions**
  - Progress through conversation
  - Verify phase indicator updates when transitioning
  - Verify transition animation (if present) is smooth
  - Check that all 4 phases are displayed correctly

- [ ] **TC2.3: Visual Design**
  - Verify phase indicator is visible at all times
  - Check color coding for different phases
  - Verify text is readable
  - Test on different screen sizes

**Expected Results:**
- Current phase is always clearly visible
- Phase transitions are reflected immediately
- Visual design is clear and professional
- Works on mobile and desktop

---

### 3. Emotion Visualization

**Location:** `app/components/EmotionVisualization.tsx`

**Requirements:** 12.2, 12.3

**Test Cases:**

- [ ] **TC3.1: Real-time Emotion Display**
  - Start a session and speak
  - Verify emotion indicator updates in real-time
  - Check that emotion type is displayed (neutral, defensive, etc.)
  - Verify confidence level is shown

- [ ] **TC3.2: Emotion Types**
  - Test with different voice tones
  - Verify all emotion types can be displayed:
    - Neutral
    - Defensive
    - Frustrated
    - Sad
    - Anxious
    - Positive

- [ ] **TC3.3: Visual Feedback**
  - Verify emotion is represented visually (color, icon, etc.)
  - Check that visualization is subtle and non-distracting
  - Verify updates are smooth, not jarring

**Expected Results:**
- Emotions are detected and displayed in real-time
- Visual representation is clear but subtle
- All emotion types are distinguishable
- Updates don't distract from conversation

---

### 4. Emotion Timeline

**Location:** `app/components/EmotionTimeline.tsx`

**Requirements:** 12.4, 12.5

**Test Cases:**

- [ ] **TC4.1: Timeline Display**
  - Complete a session
  - Verify emotion timeline is shown
  - Check that timeline shows progression over time
  - Verify time axis is labeled correctly

- [ ] **TC4.2: Emotion History**
  - Verify all detected emotions are plotted
  - Check that emotion changes are visible
  - Verify phase transitions are marked on timeline
  - Test with sessions of different lengths

- [ ] **TC4.3: Interactivity**
  - Hover over timeline points
  - Verify tooltips show emotion details
  - Check that timeline is zoomable/scrollable if needed
  - Verify timeline is readable

**Expected Results:**
- Complete emotional journey is visualized
- Timeline is easy to understand
- Phase transitions are clearly marked
- Interactive elements work smoothly

---

### 5. Development Plan Component

**Location:** `app/components/DevelopmentPlan.tsx`

**Requirements:** 8.5, 8.6

**Test Cases:**

- [ ] **TC5.1: Plan Display**
  - Complete a coaching session
  - Verify development plan is displayed
  - Check that all goals are shown
  - Verify goal details are complete (type, behavior, criteria, timeline)

- [ ] **TC5.2: Goal Editing**
  - Click edit button on a goal
  - Modify goal text
  - Save changes
  - Verify changes are persisted
  - Test canceling edits

- [ ] **TC5.3: Goal Completion**
  - Mark a goal as complete
  - Verify checkbox updates
  - Verify completion timestamp is recorded
  - Check that completed goals are visually distinct
  - Test unmarking a goal

- [ ] **TC5.4: Goal Types**
  - Verify START goals are displayed correctly
  - Verify STOP goals are displayed correctly
  - Verify CONTINUE goals are displayed correctly
  - Check that goal types are visually distinguished

**Expected Results:**
- Development plan is clear and organized
- Goals can be edited and saved
- Completion tracking works correctly
- Goal types are distinguishable

---

### 6. Session Summary

**Location:** `app/components/SessionSummary.tsx`

**Requirements:** 8.8

**Test Cases:**

- [ ] **TC6.1: Summary Display**
  - End a session
  - Verify session summary is shown
  - Check that all sections are present:
    - Session duration
    - Phases completed
    - Emotional journey
    - Key insights
    - Development plan

- [ ] **TC6.2: Summary Content**
  - Verify session duration is accurate
  - Check that phase durations are shown
  - Verify emotional journey summary is correct
  - Check that key insights are meaningful
  - Verify development plan is included

- [ ] **TC6.3: Export/Download**
  - Click download/export button
  - Verify summary is downloadable
  - Check file format (PDF or text)
  - Verify downloaded content is complete

**Expected Results:**
- Summary is comprehensive and accurate
- All session data is included
- Export functionality works
- Summary is professional and shareable

---

### 7. Conversation Transcript

**Location:** `app/components/ConversationTranscript.tsx`

**Requirements:** 8.2

**Test Cases:**

- [ ] **TC7.1: Real-time Transcript**
  - Start a session
  - Speak and listen to coach responses
  - Verify transcript updates in real-time
  - Check that user and coach messages are distinguished

- [ ] **TC7.2: Transcript Formatting**
  - Verify user messages are clearly labeled
  - Verify coach messages are clearly labeled
  - Check timestamps are shown
  - Verify text is readable and properly formatted

- [ ] **TC7.3: Scrolling**
  - Have a long conversation
  - Verify transcript auto-scrolls to latest message
  - Test manual scrolling
  - Verify scroll position is maintained when appropriate

**Expected Results:**
- Transcript updates in real-time
- User and coach messages are clearly distinguished
- Scrolling behavior is intuitive
- Text is readable and well-formatted

---

### 8. Feedback Themes Sidebar

**Location:** `app/components/FeedbackThemesSidebar.tsx`

**Requirements:** 8.8

**Test Cases:**

- [ ] **TC8.1: Themes Display**
  - Start a session with feedback
  - Verify feedback themes are shown in sidebar
  - Check that themes are categorized (strengths, improvements)
  - Verify frequency counts are shown

- [ ] **TC8.2: Theme Details**
  - Click on a theme
  - Verify theme details are shown
  - Check that example comments are displayed
  - Verify theme can be collapsed/expanded

- [ ] **TC8.3: Sidebar Behavior**
  - Verify sidebar is visible during session
  - Test collapsing/expanding sidebar
  - Check that sidebar doesn't obstruct main content
  - Test on mobile (should be collapsible)

**Expected Results:**
- Feedback themes are clearly organized
- Theme details are accessible
- Sidebar is functional and non-intrusive
- Works well on all screen sizes

---

## Mobile Responsiveness Testing

**Requirements:** 8.7

### Test Cases:

- [ ] **TC9.1: Layout Adaptation**
  - Test on mobile device or browser dev tools
  - Verify all components adapt to small screens
  - Check that no horizontal scrolling is needed
  - Verify touch targets are appropriately sized

- [ ] **TC9.2: Component Visibility**
  - Verify all essential components are accessible on mobile
  - Check that sidebars/panels can be toggled
  - Verify modals and overlays work on mobile
  - Test portrait and landscape orientations

- [ ] **TC9.3: Interaction**
  - Test touch interactions (tap, swipe, scroll)
  - Verify buttons are easily tappable
  - Check that forms are usable on mobile
  - Test voice input on mobile device

**Expected Results:**
- All components work on mobile devices
- Layout adapts appropriately
- Touch interactions are smooth
- No usability issues on small screens

---

## Integration Testing

### Test Cases:

- [ ] **TC10.1: Component Communication**
  - Verify phase indicator updates when phase changes
  - Check that emotion visualization reflects detected emotions
  - Verify development plan updates when goals are created
  - Test that all components receive real-time updates

- [ ] **TC10.2: State Management**
  - Refresh page during session
  - Verify state is preserved (if applicable)
  - Test browser back/forward buttons
  - Verify no data loss during navigation

- [ ] **TC10.3: Error Handling**
  - Disconnect from backend
  - Verify appropriate error messages
  - Test reconnection behavior
  - Verify graceful degradation

**Expected Results:**
- Components work together seamlessly
- State is managed correctly
- Errors are handled gracefully
- User experience is smooth

---

## Performance Testing

### Test Cases:

- [ ] **TC11.1: Load Time**
  - Measure initial page load time
  - Verify page loads in < 3 seconds
  - Check that components render progressively
  - Test on slow network connection

- [ ] **TC11.2: Real-time Updates**
  - Verify emotion updates don't cause lag
  - Check that transcript updates are smooth
  - Test with long sessions (20+ minutes)
  - Verify no memory leaks

- [ ] **TC11.3: Animation Performance**
  - Check that animations are smooth (60fps)
  - Verify no jank during transitions
  - Test on lower-end devices
  - Verify animations can be disabled if needed

**Expected Results:**
- Application loads quickly
- Real-time updates are performant
- Animations are smooth
- No performance degradation over time

---

## Accessibility Testing

### Test Cases:

- [ ] **TC12.1: Keyboard Navigation**
  - Navigate entire application using only keyboard
  - Verify all interactive elements are reachable
  - Check that focus indicators are visible
  - Test tab order is logical

- [ ] **TC12.2: Screen Reader**
  - Test with screen reader (VoiceOver, NVDA, etc.)
  - Verify all content is announced correctly
  - Check that dynamic updates are announced
  - Verify ARIA labels are appropriate

- [ ] **TC12.3: Visual Accessibility**
  - Test with high contrast mode
  - Verify color contrast meets WCAG standards
  - Check that information isn't conveyed by color alone
  - Test with different font sizes

**Expected Results:**
- Application is fully keyboard accessible
- Screen readers can navigate effectively
- Visual design meets accessibility standards
- No barriers for users with disabilities

---

## Test Execution Log

| Test Case | Date | Tester | Result | Notes |
|-----------|------|--------|--------|-------|
| TC1.1 | | | | |
| TC1.2 | | | | |
| TC1.3 | | | | |
| ... | | | | |

---

## Known Issues

Document any issues found during testing:

1. **Issue:** [Description]
   - **Severity:** Critical / High / Medium / Low
   - **Steps to Reproduce:** [Steps]
   - **Expected:** [Expected behavior]
   - **Actual:** [Actual behavior]
   - **Status:** Open / In Progress / Resolved

---

## Test Summary

After completing all tests, provide a summary:

- **Total Test Cases:** [Number]
- **Passed:** [Number]
- **Failed:** [Number]
- **Blocked:** [Number]
- **Pass Rate:** [Percentage]

**Overall Assessment:** [Pass / Fail / Conditional Pass]

**Recommendations:**
- [List any recommendations for improvements]

---

## Automated Testing Recommendations

For future test automation, consider:

1. **Unit Tests (Jest + React Testing Library)**
   - Component rendering tests
   - Props validation
   - Event handler tests
   - State management tests

2. **Integration Tests (Playwright / Cypress)**
   - User flow tests
   - Component interaction tests
   - API integration tests
   - Real-time update tests

3. **Visual Regression Tests (Percy / Chromatic)**
   - Component appearance tests
   - Responsive design tests
   - Theme/styling tests

4. **Performance Tests (Lighthouse CI)**
   - Load time monitoring
   - Bundle size tracking
   - Accessibility scoring
   - Best practices compliance
