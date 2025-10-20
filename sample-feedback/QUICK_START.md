# Quick Start - Testing with Sample Feedback

## Fastest Way to Test

1. **Start the application** (if not already running):
   ```bash
   # Terminal 1
   cd server && uv run bot.py --transport daily
   
   # Terminal 2
   cd client && npm run dev
   ```

2. **Open** http://localhost:3000

3. **Click "Start Session"**

4. **Upload one of these files**:
   - `feedback-example-1-mixed.json` ← **Start here!**
   - `feedback-example-2-challenging.json`
   - `feedback-example-3-positive.json`
   - `feedback-example-4-new-employee.json`
   - `feedback-example-5-simple.txt`

5. **Allow microphone access** when prompted

6. **Start talking** with the R2C2 Voice Coach!

## What to Expect

### Phase 1: Relationship Building (2-3 minutes)
- Coach introduces themselves
- Builds rapport and psychological safety
- Explains the R2C2 process
- Creates a non-judgmental space

### Phase 2: Reaction Exploration (3-5 minutes)
- Processes your emotional reactions to feedback
- Validates feelings
- Reduces defensiveness
- Helps you feel heard

### Phase 3: Content Discussion (4-6 minutes)
- Reviews specific feedback themes
- Explores strengths and areas for improvement
- Clarifies feedback meaning
- Identifies patterns

### Phase 4: Coaching for Change (5-8 minutes)
- Creates actionable development plan
- Sets SMART goals
- Identifies resources and support
- Commits to specific actions

## Tips for Testing

✅ **DO**:
- Speak naturally as if talking to a real coach
- Express genuine reactions (even if testing)
- Ask questions when confused
- Take your time processing feedback

❌ **DON'T**:
- Rush through phases
- Give one-word answers
- Skip the emotional processing
- Expect instant solutions

## Recommended Testing Sequence

1. **First test**: `feedback-example-1-mixed.json`
   - Balanced, realistic scenario
   - Good for understanding the full R2C2 process

2. **Second test**: `feedback-example-2-challenging.json`
   - Tests emotion processing capabilities
   - See how coach handles defensiveness

3. **Third test**: `feedback-example-3-positive.json`
   - Positive feedback scenario
   - Tests growth mindset development

4. **Fourth test**: `feedback-example-4-new-employee.json`
   - Developmental feedback
   - Tests encouraging, growth-oriented coaching

## Troubleshooting

**Bot not responding?**
- Check microphone permissions
- Verify server is running (http://localhost:7860)
- Check browser console for errors

**Audio issues?**
- Try Chrome or Edge browser
- Check system audio settings
- Ensure microphone is not muted

**Feedback not uploading?**
- Verify file format (JSON or TXT)
- Check file size (should be < 1MB)
- Try copy/paste instead of upload

## Need More Help?

- See `README.md` in this directory for detailed guidance
- Check main project `README.md` for troubleshooting
- Review `DEPLOYMENT.md` for configuration issues
