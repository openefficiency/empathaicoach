# Sample Feedback Data for R2C2 Voice Coach

This directory contains sample 360° feedback data files for testing the R2C2 Voice Coach application. These examples represent realistic feedback scenarios you might encounter in organizational settings.

## Available Sample Files

### 1. feedback-example-1-mixed.json
**Profile**: Alex Johnson - Senior Software Engineer
**Scenario**: Mixed feedback with strong technical skills but collaboration challenges
**Difficulty**: Moderate
**Conversation Guide**: `conversation-guide-1-mixed.md`
**Best for testing**: 
- Balanced feedback processing (both strengths and areas for improvement)
- Technical role feedback patterns
- Communication and collaboration themes
- Emotion regulation during mixed feedback

**Key themes**:
- ✅ Strengths: Technical excellence, mentorship, reliability
- ⚠️ Areas for improvement: Communication, project management, adaptability

---

### 2. feedback-example-2-challenging.json
**Profile**: Sarah Martinez - Product Manager
**Scenario**: Challenging feedback with significant interpersonal concerns
**Difficulty**: High (emotionally challenging)
**Conversation Guide**: `conversation-guide-2-challenging.md`
**Best for testing**:
- Defensive reactions and emotion processing
- Multiple critical feedback themes
- Relationship building phase effectiveness
- Coaching through difficult feedback

**Key themes**:
- ✅ Strengths: Strategic thinking, customer focus, work ethic
- ⚠️ Areas for improvement: Stakeholder management, execution, emotional regulation

**Note**: This scenario is designed to test the R2C2 framework's ability to reduce defensiveness and create psychological safety when processing difficult feedback.

---

### 3. feedback-example-3-positive.json
**Profile**: Marcus Chen - Engineering Manager
**Scenario**: Predominantly positive feedback with minor growth areas
**Difficulty**: Low
**Conversation Guide**: `conversation-guide-3-positive.md`
**Best for testing**:
- Positive feedback reinforcement
- Growth mindset development
- Transition to coaching phase
- Development planning for high performers

**Key themes**:
- ✅ Strengths: People leadership, communication, technical leadership, strategic thinking
- ⚠️ Areas for improvement: Delegation, work-life balance, cross-team collaboration

---

### 4. feedback-example-4-new-employee.json
**Profile**: Jordan Lee - UX Designer (6 months tenure)
**Scenario**: New employee with learning curve feedback
**Difficulty**: Low-Moderate
**Conversation Guide**: `conversation-guide-4-new-employee.md`
**Best for testing**:
- Growth-oriented feedback for newer employees
- Skill development themes
- Encouraging tone while addressing gaps
- Building confidence

**Key themes**:
- ✅ Strengths: Design skills, eagerness to learn, collaboration
- ⚠️ Areas for improvement: User research, systems thinking, communication, time management

---

### 5. feedback-example-5-simple.txt
**Profile**: Taylor Williams - Sales Manager
**Scenario**: Simple text format feedback
**Difficulty**: Moderate
**Conversation Guide**: `conversation-guide-5-simple.md`
**Best for testing**:
- Text format parsing (vs. JSON)
- Sales role feedback patterns
- Administrative vs. performance themes
- Manager-specific feedback

**Key themes**:
- ✅ Strengths: Client relationships, sales performance, team collaboration
- ⚠️ Areas for improvement: Administrative tasks, internal communication, coaching, work-life balance

---

## Conversation Guides

Each sample feedback file has a corresponding **conversation guide** that helps you have a meaningful dialogue with the R2C2 Voice Coach:

- `conversation-guide-1-mixed.md` - Detailed guide for balanced feedback scenarios
- `conversation-guide-2-challenging.md` - Guide for processing difficult, emotionally challenging feedback
- `conversation-guide-3-positive.md` - Guide for high performers with growth opportunities
- `conversation-guide-4-new-employee.md` - Guide for developmental feedback conversations
- `conversation-guide-5-simple.md` - Guide for high performers with administrative gaps

### What's in Each Guide

Each conversation guide includes:
- **Phase-by-phase breakdown** of what to expect and how to respond
- **Sample dialogue** showing realistic conversation flows
- **Emotional responses** you can express authentically
- **Specific goals** you might create during the coaching phase
- **Tips and best practices** for each scenario
- **Expected outcomes** from the conversation

### How to Use the Guides

1. **Before your session**: Read the guide for your chosen feedback file
2. **During your session**: Respond naturally, using the guide as inspiration (not a script)
3. **After your session**: Compare your experience to the expected outcomes

**Important**: The guides are meant to help you engage authentically, not to script your responses. The R2C2 coach adapts to your actual reactions, so be genuine!

---

## How to Use These Files

### Testing in the Application

1. **Start the R2C2 Voice Coach**:
   ```bash
   # Terminal 1: Start server
   cd server
   uv run bot.py --transport daily
   
   # Terminal 2: Start client
   cd client
   npm run dev
   ```

2. **Upload Feedback**:
   - Open http://localhost:3000
   - Click "Start Session"
   - Upload one of the sample feedback files
   - Or copy/paste the content into the text area

3. **Experience the R2C2 Process**:
   - **Relationship**: Notice how the coach builds rapport
   - **Reaction**: Observe emotion detection and processing
   - **Content**: See how feedback themes are explored
   - **Coaching**: Experience development plan creation

### Testing Different Scenarios

**For Defensive Reactions**:
- Use `feedback-example-2-challenging.json`
- Pay attention to how the coach handles emotional responses
- Test the relationship building and reaction phases

**For Positive Reinforcement**:
- Use `feedback-example-3-positive.json`
- Notice how strengths are celebrated
- Focus on growth areas without diminishing achievements

**For New Employees**:
- Use `feedback-example-4-new-employee.json`
- Observe developmental, growth-oriented coaching
- Test encouragement while addressing skill gaps

**For Format Testing**:
- Use `feedback-example-5-simple.txt`
- Verify text format parsing works correctly
- Test with different formatting styles

## File Formats Supported

### JSON Format
Structured format with detailed metadata:
```json
{
  "employee": { ... },
  "feedback_summary": { ... },
  "strengths": [ ... ],
  "areas_for_improvement": [ ... ],
  "specific_incidents": [ ... ],
  "manager_notes": "..."
}
```

### Text Format
Simple, human-readable format:
```
360° FEEDBACK REPORT
Employee: Name
Role: Title

=== STRENGTHS ===
Theme (mentioned by X people):
- "Quote 1"
- "Quote 2"

=== AREAS FOR IMPROVEMENT ===
Theme (mentioned by X people):
- "Quote 1"
- "Quote 2"
```

## Creating Your Own Test Data

### Guidelines for Realistic Feedback

1. **Include Both Strengths and Areas for Improvement**
   - Real feedback is rarely all positive or all negative
   - Aim for 2-4 strength themes and 2-4 improvement themes

2. **Use Specific Examples**
   - Include concrete incidents and behaviors
   - Avoid vague statements like "needs to improve communication"
   - Better: "Could improve at providing context when requesting work"

3. **Vary Frequency and Intensity**
   - Some themes mentioned by many people (high frequency)
   - Others mentioned by few (lower frequency)
   - Mix of minor concerns and significant issues

4. **Include Multiple Perspectives**
   - Manager feedback
   - Peer feedback
   - Direct report feedback (if applicable)
   - Cross-functional feedback

5. **Consider Emotional Impact**
   - Some feedback will be harder to hear than others
   - Include both validating and challenging content
   - Think about what might trigger defensiveness

### Template for JSON Format

```json
{
  "employee": {
    "name": "Employee Name",
    "role": "Job Title",
    "department": "Department",
    "tenure": "X years/months"
  },
  "feedback_summary": {
    "overall_rating": 3.5,
    "total_responses": 10,
    "response_breakdown": {
      "manager": 1,
      "peers": 6,
      "direct_reports": 3
    }
  },
  "strengths": [
    {
      "theme": "Theme Name",
      "frequency": 8,
      "comments": [
        "Specific positive comment 1",
        "Specific positive comment 2"
      ]
    }
  ],
  "areas_for_improvement": [
    {
      "theme": "Theme Name",
      "frequency": 5,
      "comments": [
        "Specific developmental comment 1",
        "Specific developmental comment 2"
      ]
    }
  ],
  "specific_incidents": [
    {
      "type": "positive",
      "description": "Specific positive incident"
    },
    {
      "type": "concern",
      "description": "Specific concerning incident"
    }
  ],
  "manager_notes": "Summary and context from manager"
}
```

## Testing Checklist

Use this checklist when testing with sample feedback:

- [ ] Upload/paste feedback successfully
- [ ] Session starts and bot connects
- [ ] Relationship phase: Coach builds rapport
- [ ] Reaction phase: Emotions are detected and processed
- [ ] Content phase: Feedback themes are discussed
- [ ] Coaching phase: Development plan is created
- [ ] Emotion visualization displays correctly
- [ ] Transcript captures conversation accurately
- [ ] Development plan includes SMART goals
- [ ] Session can be saved and exported
- [ ] Audio quality is clear
- [ ] Bot responds appropriately to emotional cues
- [ ] Phase transitions happen naturally
- [ ] Final summary is comprehensive

## Privacy Note

These sample files contain fictional data created for testing purposes only. No real employee data should be used for testing or development. When deploying to production, ensure proper data privacy and security measures are in place for handling actual 360° feedback data.

## Contributing

To add new sample feedback files:

1. Create a realistic scenario based on common feedback patterns
2. Use the JSON or text format templates above
3. Include a mix of strengths and development areas
4. Add specific, behavioral examples
5. Update this README with the new file description
6. Test the file in the application to ensure it works correctly

## Questions or Issues?

If you encounter issues with the sample data or have suggestions for additional scenarios, please refer to the main project README or open an issue.
