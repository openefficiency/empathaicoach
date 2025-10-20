# **EmpathAI Coach**

## **1\. What is this?**

**EmpathAI Coach** is an AI-powered feedback facilitation system that transforms how people receive 360-degree feedback. Instead of just delivering feedback (which often triggers defensiveness and decreases performance), our voice AI conducts personalized conversations using the R2C2 Model-a research-validated framework from healthcare education with 6,000+ citations.

The system detects emotional reactions in real-time and validates feelings _before_ sharing critical feedback details, ensuring recipients stay open and engaged rather than defensive. It guides users through four structured phases: Relationship building, Reaction exploration, Content review, and Coaching for action-ultimately generating concrete development plans that people actually follow.

**The problem:** Research shows 1 in 3 feedback interventions actually harm performance because they trigger defensive reactions.

**Our solution:** First voice AI that facilitates emotional processing using neuroscience-backed conversational frameworks, converting defensive reactions into actionable growth.

## **2\. Demo Video (120 seconds)**

https://youtu.be/sM5E71fKzeA



## **3\. Project workflow and tools**

### **Gemini 2.5 Flash (Multimodal AI)**

- **Real-time Emotion Detection**: Gemini analyzes user voice transcripts to detect defensiveness, openness, and curiosity through linguistic markers (justification language like "but I...", tone indicators, question patterns). Returns structured JSON with emotion scores (0.0-1.0).
- **Phase-Aware Response Generation**: Gemini generates contextually appropriate responses based on the current R2C2 phase. Each phase has a specialized system prompt:
  - Phase 1: Trust-building, empathetic opening
  - Phase 2: Emotion validation, defensiveness handling (most critical)
  - Phase 3: Specific feedback delivery with diagnostic questions
  - Phase 4: Action-oriented coaching and planning
- **Adaptive Conversation Flow**: Gemini determines when to transition between phases by analyzing user readiness signals (curiosity emerging, defensiveness reducing, explicit requests for details).
- **Structured Output Generation**: Gemini creates SMART action plans in JSON format based on conversation insights, ensuring specific, measurable, achievable commitments.

### **Pipecat (Voice AI Infrastructure)**

- **Low-Latency Voice Pipeline**: Pipecat's Daily.co integration provides real-time WebRTC voice streaming with <300ms latency, making conversations feel natural rather than robotic.
- **Voice Activity Detection (VAD)**: Configured VAD with 0.8s stop detection to allow natural pauses for emotional processing without cutting off users mid-thought.
- **Streaming Response Architecture**: Pipecat streams Gemini responses in real-time rather than waiting for complete generation, maintaining conversational flow.
- **Pipeline Processing**: Built custom processors in Pipecat's pipeline architecture:
  - LLMUserResponseAggregator: Collects complete user utterances
  - EmotionAnalyzer: Analyzes responses and routes to state machine
  - ResponseValidator: Ensures AI responses follow phase-specific rules

### **Integration Architecture**

- User Voice → Pipecat VAD → Transcript → Gemini Emotion Analysis
- ↓
- R2C2 State Machine
- ↓
- Phase-Specific Prompt → Gemini Response
- ↓

Pipecat TTS → User

**Key Innovation**: The combination of Gemini's multimodal understanding and Pipecat's conversational infrastructure enables _emotion-adaptive_ AI that dynamically adjusts its approach based on psychological markers-something impossible with static prompt engineering alone.


### Technology Stack <br>

*Backend:* <br>
- Python 3.10+ <br>
- Pipecat AI framework (real-time audio pipeline) <br>
- Google Gemini 2.5 Flash (multimodal AI with native audio) <br>
- Daily.co (WebRTC transport) <br>
- SQLite (data persistence) <br>
- FastAPI (HTTP endpoints) <br>

*Frontend:* <br>
- Next.js 15.5+ <br>
- Pipecat Voice UI Kit <br>
- TypeScript <br>
- Tailwind CSS 4 <br>

## **4\. What We Did New During the Hackathon**

### **Built from Scratch (100% New)**

- **R2C2 State Machine Engine** (r2c2_engine.py)
  - 4-phase conversational state machine with automatic transition logic
  - Emotion detection algorithms analyzing 15+ linguistic markers
  - Phase-specific system prompt generation (4 distinct templates, ~500 words each)
  - Defensive reaction counter and validation tracking
  - Conversation transcript management with phase tagging
- **Pipecat Integration** (main_with_state_machine.py)
  - Voice pipeline connecting Daily.co → Gemini → R2C2 state machine
  - Custom analyze_and_route processor for real-time emotion analysis
  - WebSocket broadcast system for UI updates
  - VAD configuration optimized for emotional conversation (0.8s pauses)
- **Gemini Emotion Analyzer** (emotion_analyzer.py)
  - Structured JSON prompt for emotion scoring (defensiveness, openness, curiosity)
  - Validation-needed flag detection
  - Fallback logic for JSON parsing errors
  - Real-time emotion detection (<500ms response time)
- **Web Dashboard** (index.html + visualizations.js)
  - Live transcript with speaker identification
  - Animated emotion meters (3 gauges: defensiveness, openness, curiosity)
  - 4-phase progress indicator with transition animations
  - Session context panel (role, theme, rating gap)
  - Action plan generator
  - Typewriter effect for transcript entries
  - Pulse animations on phase transitions
- **Feedback Scenario Database** (feedback_scenarios.json)
  - 3 realistic 360-feedback scenarios:
    - Defensive Product Manager (communication gaps)
    - Growth-minded Engineering Lead (delegation issues)
    - Resistant Senior Designer (collaboration feedback)
  - Each with self-ratings, team ratings, positive/constructive themes, anonymous quotes
  - Expected defensiveness triggers for testing
- **Advanced Prompt Templates** (prompts.py)
  - 4 phase-specific system prompts (1,500+ words total)
  - Phase 2 defensive response library (8+ validation phrases)
  - SMART action plan template structure
  - Transition signal detection logic
  - Forbidden phrase detection for phase violations
- **Response Validator** (response_validator.py)
  - Enforces phase-specific conversation rules
  - Detects premature content sharing in Phase 2
  - Validates emotion validation when defensiveness detected
  - Action-orientation checker for Phase 4
- **Demo Testing Suite** (test_demo.py)
  - Automated scenario testing with simulated user responses
  - 2 pre-built test flows (defensive vs. growth-minded personas)
  - Emotion score verification
  - Phase transition validation
- **5-Slide Pitch Deck**
  - Problem: \$6B wasted on harmful feedback
  - Research: R2C2 Model from healthcare (6,000 citations)
  - Technology: Gemini + Pipecat architecture
  - Business: B2B SaaS, \$50-200/employee/year, 10M+ managers TAM
  - Demo setup slide: <https://bit.ly/EmpathAI>
- **Documentation**
  - Hour-by-hour implementation guide (8.5 hours)
  - Setup scripts (setup_daily.py, test_daily_connection.py)
  - Emergency troubleshooting playbook
  - Pitch script (2 minutes)
  - Demo script (3 minutes with judge participation)

### **Research Foundation (Pre-Hackathon)**

We did conduct 100+ hours of research _before_ the hackathon analyzing 28 feedback frameworks, which informed our R2C2 implementation. However, **all code, configuration, UI, and documentation was built during the hackathon**. The research gave us domain expertise, but the engineering was 100% new.

### **What Makes This Innovative**

- **First voice AI** applying research-validated feedback frameworks (R2C2, not generic chatbots)
- **Emotion-adaptive conversation** that dynamically stays in validation phase until defensiveness reduces
- **Real-time psychological marker detection** using Gemini's language understanding
- **Phase-aware state machine** ensuring proper emotional processing sequence
- **Live emotion visualization** showing defensiveness/openness shifts during conversation

## **5\. Feedback on Tools**

### **Gemini 2.5 Flash: ⭐⭐⭐⭐⭐ (5/5)**

**What Worked Exceptionally Well:**

- **Streaming performance**: <500ms response time for emotion analysis and generation-critical for natural conversation flow
- **Structured output**: JSON mode worked reliably for emotion scoring (though we added fallback parsing for safety)
- **Contextual understanding**: Excellent at detecting subtle defensiveness markers ("but I...", "nobody told me") and differentiating from curiosity
- **System prompt adherence**: Followed phase-specific instructions well, especially complex Phase 2 validation rules
- **Multimodal capability**: While we focused on text transcripts, knowing voice tone analysis is possible opens future enhancement paths

**Constructive Feedback:**

- **JSON extraction**: Occasionally wrapped JSON in markdown code blocks (\`\`\`json), requiring manual stripping. Would love a strict JSON-only mode flag.
- **Prompt length limits**: Phase 2 system prompts approached token limits when including conversation history. Documentation on exact context windows for streaming would help optimize.
- **Cost transparency**: Unclear on per-request pricing during rapid testing. Real-time cost estimator in API response would enable better budgeting.

**Feature Requests:**

- **Emotion detection API**: Pre-built emotion classification endpoint would be valuable (we built custom prompts, but a specialized model could be faster/more accurate)
- **Voice tone analysis**: Direct audio input for prosody/tone analysis would enhance defensiveness detection beyond transcript alone

### **Pipecat: ⭐⭐⭐⭐½ (4.5/5)**

**What Worked Exceptionally Well:**

- **Daily.co integration**: Seamless WebRTC setup-room connection took <10 lines of code
- **Pipeline architecture**: Modular processor design made custom logic integration elegant
- **VAD quality**: Voice activity detection worked reliably, even with emotional pauses
- **Documentation**: Examples and quickstart guides were clear and actionable
- **Streaming support**: Real-time response streaming from Gemini felt natural in conversation

**Constructive Feedback:**

- **Error messages**: Some connection failures gave generic errors. More specific troubleshooting hints (e.g., "Room URL format invalid" vs. "Connection failed") would speed debugging.
- **State management**: No built-in conversation state persistence. We built our own transcript/state tracking, but a provided ConversationMemory class would help newcomers.
- **Testing mode**: No easy way to simulate voice input for automated testing without actual Daily.co calls (cost concern during development). Mock transport would be valuable.

**Feature Requests:**

- **Emotion analyzer processor**: Pre-built processor for sentiment/emotion detection from text/audio would complement LLM integration
- **Phase management**: Built-in state machine or wizard-flow helper for multi-stage conversations (we built custom R2C2 engine, but common pattern)
- **UI components**: Optional React components for transcript display, connection status, etc., would accelerate frontend development

### **Daily.co: ⭐⭐⭐⭐⭐ (5/5)**

**What Worked Exceptionally Well:**

- **Room setup**: Creating public demo room took 2 minutes via dashboard
- **Audio quality**: Crystal clear voice transmission with minimal latency
- **Free tier**: Generous for hackathon prototyping
- **iframe embed**: Easy to integrate into web UI

**Minor Note:**

- **Token vs. API key confusion**: Documentation could more clearly distinguish when DAILY_TOKEN (for room access) vs. DAILY_API_KEY (for room management) is needed. We initially thought both were required for basic usage.

### **Overall Tool Ecosystem: ⭐⭐⭐⭐⭐**

The combination of **Gemini + Pipecat + Daily.co** enabled us to build a sophisticated voice AI application in <9 hours. Each tool excelled at its specific role:

- **Gemini**: Intelligence layer (emotion detection, adaptive responses)
- **Pipecat**: Conversation infrastructure (streaming, VAD, pipeline)
- **Daily.co**: Voice transport (WebRTC, audio quality)

This is exactly the kind of integrated stack that makes rapid voice AI prototyping feasible. Our main time sink was domain logic (R2C2 state machine), not fighting with tools-which is the mark of great developer experience.
