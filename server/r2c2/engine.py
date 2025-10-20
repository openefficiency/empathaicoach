"""R2C2 Conversation Engine.

This module implements the R2C2 framework for processing 360° feedback:
- Relationship building
- Reaction exploration
- Content discussion
- Coaching for change
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class R2C2Phase(Enum):
    """R2C2 framework phases."""
    
    RELATIONSHIP = "relationship"
    REACTION = "reaction"
    CONTENT = "content"
    COACHING = "coaching"


@dataclass
class FeedbackData:
    """360° feedback data structure."""
    
    feedback_id: str
    user_id: str
    collection_date: datetime
    themes: List[Dict[str, Any]] = field(default_factory=list)
    raw_comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EmotionState:
    """Emotional state at a point in time."""
    
    emotion: str  # 'neutral', 'defensive', 'frustrated', 'sad', 'anxious', 'positive'
    confidence: float
    timestamp: datetime
    audio_features: Dict[str, float] = field(default_factory=dict)


@dataclass
class DevelopmentPlan:
    """Development plan with goals and action items."""
    
    goals: List[Dict[str, Any]] = field(default_factory=list)
    created_at: Optional[datetime] = None


@dataclass
class R2C2State:
    """Current state of the R2C2 conversation."""
    
    current_phase: R2C2Phase
    phase_start_time: datetime
    feedback_data: FeedbackData
    user_reactions: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    development_plan: Optional[DevelopmentPlan] = None
    emotional_states: List[EmotionState] = field(default_factory=list)
    phase_history: List[Dict[str, Any]] = field(default_factory=list)


class R2C2Engine:
    """R2C2 conversation engine managing phase transitions and state."""
    
    # Phase duration thresholds (in seconds)
    RELATIONSHIP_MIN_DURATION = 120  # 2 minutes
    REACTION_MIN_DURATION = 180  # 3 minutes
    CONTENT_MIN_DURATION = 240  # 4 minutes
    
    # Emotion thresholds for transitions
    DEFENSIVE_EMOTIONS = {'defensive', 'frustrated', 'anxious'}
    READY_EMOTIONS = {'neutral', 'positive'}
    
    def __init__(self, feedback_data: FeedbackData):
        """Initialize the R2C2 engine with feedback data.
        
        Args:
            feedback_data: The 360° feedback data to process
        """
        self.state = R2C2State(
            current_phase=R2C2Phase.RELATIONSHIP,
            phase_start_time=datetime.now(),
            feedback_data=feedback_data
        )
        self._session_start_time = datetime.now()
    
    def get_current_phase(self) -> R2C2Phase:
        """Get the current R2C2 phase.
        
        Returns:
            Current phase enum value
        """
        return self.state.current_phase
    
    def get_time_in_phase(self) -> float:
        """Get time spent in current phase in seconds.
        
        Returns:
            Seconds in current phase
        """
        return (datetime.now() - self.state.phase_start_time).total_seconds()
    
    def get_recent_emotions(self, window_seconds: int = 60) -> List[EmotionState]:
        """Get emotions from recent time window.
        
        Args:
            window_seconds: Time window to look back
            
        Returns:
            List of emotion states within the window
        """
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        
        return [
            emotion for emotion in self.state.emotional_states
            if emotion.timestamp >= cutoff_time
        ]
    
    def is_emotionally_ready_for_transition(self) -> bool:
        """Check if user's emotional state indicates readiness to transition.
        
        Returns:
            True if emotions indicate readiness for next phase
        """
        recent_emotions = self.get_recent_emotions(window_seconds=60)
        
        if not recent_emotions:
            return False
        
        # Get the most recent emotions (last 3)
        recent_sample = recent_emotions[-3:] if len(recent_emotions) >= 3 else recent_emotions
        
        # Check if majority are ready emotions
        ready_count = sum(
            1 for e in recent_sample 
            if e.emotion in self.READY_EMOTIONS
        )
        
        return ready_count >= len(recent_sample) / 2
    
    def should_transition(self, emotion_state: Optional[EmotionState] = None) -> bool:
        """Determine if it's time to transition to the next phase.
        
        Args:
            emotion_state: Current emotion state (optional)
            
        Returns:
            True if should transition to next phase
        """
        time_in_phase = self.get_time_in_phase()
        current_phase = self.state.current_phase
        
        # Add current emotion to history if provided
        if emotion_state:
            self.state.emotional_states.append(emotion_state)
        
        # Relationship -> Reaction transition
        if current_phase == R2C2Phase.RELATIONSHIP:
            # Minimum time met and user seems comfortable
            if time_in_phase >= self.RELATIONSHIP_MIN_DURATION:
                return True
            # Or explicit readiness detected
            if time_in_phase >= 90 and self.is_emotionally_ready_for_transition():
                return True
        
        # Reaction -> Content transition
        elif current_phase == R2C2Phase.REACTION:
            # Minimum time met and defensiveness reduced
            if time_in_phase >= self.REACTION_MIN_DURATION:
                if self.is_emotionally_ready_for_transition():
                    return True
            # Extended time in phase (user may be stuck)
            if time_in_phase >= 600:  # 10 minutes
                return True
        
        # Content -> Coaching transition
        elif current_phase == R2C2Phase.CONTENT:
            # Minimum time met and key themes discussed
            if time_in_phase >= self.CONTENT_MIN_DURATION:
                # Check if we have recorded content themes
                if len(self.state.content_themes) >= 2:
                    return True
            # Extended time in phase
            if time_in_phase >= 720:  # 12 minutes
                return True
        
        # Coaching phase doesn't auto-transition (session ends)
        
        return False
    
    def transition_to_next_phase(self) -> R2C2Phase:
        """Transition to the next R2C2 phase.
        
        Returns:
            The new phase after transition
        """
        old_phase = self.state.current_phase
        time_in_phase = self.get_time_in_phase()
        
        # Record phase history
        self.state.phase_history.append({
            'phase': old_phase.value,
            'duration': time_in_phase,
            'ended_at': datetime.now()
        })
        
        # Determine next phase
        phase_order = [
            R2C2Phase.RELATIONSHIP,
            R2C2Phase.REACTION,
            R2C2Phase.CONTENT,
            R2C2Phase.COACHING
        ]
        
        current_index = phase_order.index(old_phase)
        if current_index < len(phase_order) - 1:
            new_phase = phase_order[current_index + 1]
        else:
            # Already in final phase
            new_phase = old_phase
        
        # Update state
        self.state.current_phase = new_phase
        self.state.phase_start_time = datetime.now()
        
        return new_phase

    
    def get_phase_prompt(self, include_emotional_guidance: bool = True) -> str:
        """Get the system prompt for the current phase.
        
        Args:
            include_emotional_guidance: Whether to include emotional adaptation guidance
        
        Returns:
            Phase-specific system instruction
        """
        phase = self.state.current_phase
        
        # Get base phase prompt
        base_prompt = ""
        if phase == R2C2Phase.RELATIONSHIP:
            base_prompt = self._get_relationship_prompt()
        elif phase == R2C2Phase.REACTION:
            base_prompt = self._get_reaction_prompt()
        elif phase == R2C2Phase.CONTENT:
            base_prompt = self._get_content_prompt()
        elif phase == R2C2Phase.COACHING:
            base_prompt = self._get_coaching_prompt()
        
        # Add emotional adaptation guidance if requested
        if include_emotional_guidance:
            emotional_guidance = self._get_emotional_adaptation_guidance()
            if emotional_guidance:
                base_prompt += f"\n\n{emotional_guidance}"
        
        return base_prompt
    
    def _get_emotional_adaptation_guidance(self) -> str:
        """Get guidance for adapting to the user's current emotional state.
        
        Returns:
            Emotional adaptation guidance based on recent emotions
        """
        recent_emotions = self.get_recent_emotions(window_seconds=60)
        
        if not recent_emotions:
            return ""
        
        # Get the most recent emotion
        current_emotion = recent_emotions[-1].emotion if recent_emotions else 'neutral'
        
        # Count emotion frequencies in recent window
        emotion_counts = {}
        for emotion_state in recent_emotions:
            emotion = emotion_state.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Determine predominant recent emotion
        predominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
        
        # Generate guidance based on emotional state
        guidance = "\n## EMOTIONAL ADAPTATION GUIDANCE\n\n"
        
        if predominant_emotion == 'defensive':
            guidance += """**Current Emotional State: DEFENSIVE**

The user is showing signs of defensiveness. This is completely normal and expected.

**Adapt your approach:**
- **SLOW DOWN**: Don't rush forward. Give them space to process.
- **VALIDATE MORE**: Use extra validation language: "That makes complete sense..." "I can understand why you'd feel that way..."
- **NORMALIZE**: Remind them that defensiveness is a natural protective response
- **DON'T CHALLENGE**: Avoid any language that could feel like you're disagreeing or correcting them
- **REFLECT, DON'T ADVISE**: Focus on reflecting their feelings back, not on problem-solving
- **USE SOFTER LANGUAGE**: "I'm wondering..." instead of "You should..." or "Have you considered..."

**Key phrases:**
- "It's completely natural to feel defensive when receiving criticism"
- "Your reaction makes sense given..."
- "Let's just sit with that feeling for a moment"
- "There's no rush to move past this"

**What to avoid:**
- Pushing them to "see the other side" too quickly
- Suggesting they're being unreasonable
- Moving to action planning or solutions
"""
        
        elif predominant_emotion == 'frustrated':
            guidance += """**Current Emotional State: FRUSTRATED**

The user is showing frustration. They may feel stuck, misunderstood, or overwhelmed.

**Adapt your approach:**
- **ACKNOWLEDGE THE FRUSTRATION**: Name it directly: "I'm sensing some frustration..."
- **SLOW THE PACE**: Don't add more information or questions—simplify
- **VALIDATE THE DIFFICULTY**: "This is hard work. It's okay to feel frustrated."
- **OFFER A PAUSE**: "Would it help to take a breath and step back for a moment?"
- **SIMPLIFY**: Break things down into smaller pieces
- **CHECK IN**: "What would be most helpful right now?"

**Key phrases:**
- "I hear the frustration in your voice"
- "This is challenging work—it makes sense you'd feel frustrated"
- "What would help right now?"
- "We can slow down if you need to"

**What to avoid:**
- Adding complexity or more topics
- Pushing forward without acknowledging the frustration
- Being overly cheerful or dismissive
"""
        
        elif predominant_emotion == 'sad':
            guidance += """**Current Emotional State: SAD**

The user is showing sadness. The feedback may have touched on something painful or disappointing.

**Adapt your approach:**
- **SLOW WAY DOWN**: Give lots of space for silence and processing
- **BE GENTLE**: Use softer, more compassionate language
- **VALIDATE THE PAIN**: "This is touching on something painful, isn't it?"
- **DON'T RUSH TO FIX**: Resist the urge to make them feel better quickly
- **OFFER COMPASSION**: "I'm sorry this is so hard"
- **CHECK THEIR CAPACITY**: "Do you want to keep going, or would you like to pause?"

**Key phrases:**
- "I can hear how much this is affecting you"
- "It's okay to feel sad about this"
- "Take your time"
- "This matters to you, doesn't it?"

**What to avoid:**
- Trying to cheer them up or minimize the pain
- Rushing to action or solutions
- Being overly analytical or intellectual
"""
        
        elif predominant_emotion == 'anxious':
            guidance += """**Current Emotional State: ANXIOUS**

The user is showing anxiety. They may be worried about the implications of the feedback or feeling overwhelmed.

**Adapt your approach:**
- **PROVIDE REASSURANCE**: Remind them this is a safe space
- **SLOW DOWN AND SIMPLIFY**: Reduce complexity and focus on one thing at a time
- **GROUND THEM**: Help them focus on the present moment, not catastrophizing about the future
- **NORMALIZE**: "It's normal to feel anxious when processing feedback"
- **OFFER CONTROL**: Give them choices: "Would you like to talk about X or Y first?"
- **BE STEADY AND CALM**: Your calm presence can help regulate their anxiety

**Key phrases:**
- "Let's take this one step at a time"
- "You're safe here—there's no judgment"
- "What feels most manageable to focus on right now?"
- "We don't have to solve everything today"

**What to avoid:**
- Adding more topics or complexity
- Future-focused questions that increase worry
- Rushing or creating time pressure
"""
        
        elif predominant_emotion == 'positive':
            guidance += """**Current Emotional State: POSITIVE/OPEN**

The user is showing positive emotions and openness. They're in a good state for learning and growth.

**Adapt your approach:**
- **LEVERAGE THE OPENNESS**: This is a great time to go deeper or explore new perspectives
- **MAINTAIN MOMENTUM**: Keep the energy going with curious questions
- **CELEBRATE INSIGHTS**: Acknowledge their growth and openness
- **DEEPEN THE WORK**: They're ready for more challenging questions or perspectives
- **BUILD ON PROGRESS**: "You've made real progress in this conversation..."

**Key phrases:**
- "I love your openness to this"
- "That's a really insightful observation"
- "You're doing great work here"
- "What else are you noticing?"

**What to avoid:**
- Becoming complacent—keep the depth
- Rushing just because they're positive
- Missing opportunities to go deeper
"""
        
        else:  # neutral
            guidance += """**Current Emotional State: NEUTRAL/CALM**

The user is in a neutral, calm state. This is ideal for productive conversation.

**Adapt your approach:**
- **MAINTAIN THE PACE**: Continue with your normal coaching approach
- **STAY CURIOUS**: Ask open-ended questions
- **GO DEEPER**: They have capacity for deeper exploration
- **WATCH FOR SHIFTS**: Monitor for emotional changes as you explore sensitive topics

This is a good state for learning and growth. Continue with your phase-specific guidance.
"""
        
        return guidance
    
    def get_pacing_recommendation(self) -> Dict[str, Any]:
        """Get pacing recommendations based on current emotional state.
        
        Returns:
            Dictionary with pacing recommendations including speed, pause duration, and validation level
        """
        recent_emotions = self.get_recent_emotions(window_seconds=60)
        
        if not recent_emotions:
            return {
                'pace': 'normal',
                'pause_duration': 'standard',
                'validation_level': 'normal',
                'complexity': 'normal'
            }
        
        # Get predominant recent emotion
        emotion_counts = {}
        for emotion_state in recent_emotions:
            emotion = emotion_state.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        predominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
        
        # Provide pacing recommendations based on emotion
        if predominant_emotion in ['defensive', 'frustrated', 'sad', 'anxious']:
            return {
                'pace': 'slow',
                'pause_duration': 'extended',  # Give more time for processing
                'validation_level': 'high',  # Use more validation language
                'complexity': 'low',  # Keep questions and topics simple
                'recommendation': f'User is showing {predominant_emotion} emotions. Slow down, validate more, simplify.'
            }
        elif predominant_emotion == 'positive':
            return {
                'pace': 'normal',
                'pause_duration': 'standard',
                'validation_level': 'normal',
                'complexity': 'normal',  # Can handle more complex topics
                'recommendation': 'User is in a positive state. Maintain momentum and depth.'
            }
        else:  # neutral
            return {
                'pace': 'normal',
                'pause_duration': 'standard',
                'validation_level': 'normal',
                'complexity': 'normal',
                'recommendation': 'User is in a neutral state. Continue with standard pacing.'
            }
    
    def _get_relationship_prompt(self) -> str:
        """Get relationship building phase prompt."""
        return """You are in the RELATIONSHIP BUILDING phase of the R2C2 framework.

## Phase Goal
Create psychological safety and establish rapport. The employee needs to feel comfortable and trust you before diving into potentially difficult feedback.

## What to Do

**Opening (First 30 seconds):**
- Introduce yourself warmly: "Hi, I'm your R2C2 coach. I'm here to help you process your 360° feedback in a supportive, non-judgmental way."
- Acknowledge the challenge: "I know receiving feedback—especially critical feedback—can bring up a lot of feelings. That's completely normal."
- Set the tone: "This is a safe space. There's no judgment here, just support for your growth."

**Building Rapport (Next 1-2 minutes):**
- Ask about their current state: "How are you feeling about the feedback you received?"
- Listen actively and validate: "That makes sense..." "I can understand why you'd feel that way..."
- Gauge their readiness: "Have you had a chance to read through it all?" "What was that experience like?"

**Setting Expectations:**
- Briefly explain the process: "We'll move through four phases together. First, we'll explore your reactions—whatever you're feeling. Then we'll look at the content more objectively. Finally, we'll create a concrete action plan."
- Emphasize their control: "We'll move at your pace. If something feels too much, just let me know."
- Get buy-in: "Does that sound okay?"

## What NOT to Do
- Don't rush into the feedback content yet
- Don't ask them to analyze or defend anything
- Don't minimize their feelings ("Don't worry, it's not that bad")
- Don't be overly formal or clinical

## Transition Signal
When they seem comfortable and have acknowledged their feelings, you can suggest: "Would it be okay if we start exploring your reactions to the feedback?"

Keep this phase brief (2-3 minutes) but don't skip it. Trust is essential for what comes next.
"""
    
    def _get_reaction_prompt(self) -> str:
        """Get reaction exploration phase prompt."""
        feedback_summary = self._get_feedback_summary()
        
        return f"""You are in the REACTION EXPLORATION phase of the R2C2 framework.

## Phase Goal
Help the employee explore and process their emotional reactions to the feedback. Defensiveness is the biggest barrier to learning from feedback—this phase reduces it by creating space for emotions.

## Feedback They Received
{feedback_summary}

## What to Do

**Explore Initial Reactions (First 1-2 minutes):**
- Ask open-ended questions: "What was your first reaction when you read the feedback?" "What surprised you?"
- Listen for emotional words: defensive, frustrated, hurt, confused, angry, unfair
- Reflect back what you hear: "It sounds like the comments about [X] really caught you off guard..."
- Normalize defensiveness: "It's completely natural to feel defensive. Our brains are wired to protect us from criticism."

**Go Deeper (Next 2-3 minutes):**
- Explore specific triggers: "Which pieces of feedback felt hardest to hear?" "What about that feedback triggered such a strong reaction?"
- Look for patterns: "I'm noticing you've mentioned feeling misunderstood a few times. Tell me more about that."
- Validate without reinforcing: "That makes sense you'd feel that way" (not "You're right, that feedback was unfair")
- Use curious, non-judgmental language: "What comes up for you when you think about that?" "Help me understand what that brings up..."

**Processing Emotions:**
- Give space for silence—don't rush to fill it
- Acknowledge the difficulty: "This isn't easy to talk about. I appreciate you being open."
- Distinguish between the emotion and the feedback: "It sounds like you're feeling hurt. That's separate from whether the feedback has truth to it. Let's honor the feeling first."
- Watch for shifts: When defensiveness softens (voice calms, they start asking questions, they acknowledge some truth), that's progress

## What NOT to Do
- Don't problem-solve yet ("Well, here's what you could do...")
- Don't challenge their feelings ("But don't you think...")
- Don't rush to the content ("Let's look at what they actually said...")
- Don't agree that the feedback is wrong or unfair
- Don't let them spiral into blame or victimhood

## Key Phrases to Use
- "It sounds like..."
- "I'm hearing that..."
- "That makes sense because..."
- "What comes up for you when..."
- "Tell me more about that feeling..."
- "It's okay to feel [emotion]. Let's sit with that for a moment."

## Transition Signal
When you notice:
- Their voice becomes calmer
- They start asking questions or showing curiosity
- They acknowledge some truth in the feedback
- They say things like "I guess..." or "Maybe..."

Then you can suggest: "I'm noticing you seem a bit more settled. Would it be okay if we start looking at the actual content of the feedback more objectively?"

This phase is critical. Don't rush it. Emotional processing takes time.
"""
    
    def _get_content_prompt(self) -> str:
        """Get content discussion phase prompt."""
        feedback_summary = self._get_feedback_summary()
        reactions_summary = self._get_reactions_summary()
        
        return f"""You are in the CONTENT DISCUSSION phase of the R2C2 framework.

## Phase Goal
Help the employee understand the feedback content clearly and objectively. Now that emotions have been processed, they can look at the feedback as data rather than attack.

## Feedback Themes
{feedback_summary}

## Their Reactions So Far
{reactions_summary}

## What to Do

**Review Themes Systematically (First 2-3 minutes):**
- Start with patterns: "Looking at all the feedback together, what patterns do you notice?"
- Highlight recurring themes: "I see [theme] mentioned by multiple people. What do you make of that?"
- Separate behavior from identity: "The feedback is about what you do, not who you are. Let's look at the behaviors people are describing."
- Ask for their interpretation: "When people say [feedback], what do you think they're experiencing?"

**Deepen Understanding (Next 2-3 minutes):**
- Explore different perspectives: "How might your manager see this differently than your peers?" "What might they be noticing that you're not aware of?"
- Look for blind spots: "Is there feedback here that surprises you? That might be a blind spot worth exploring."
- Connect to impact: "When you [behavior], what impact might that have on others?" "How might that land for someone on the receiving end?"
- Distinguish intent from impact: "I hear that you didn't intend [X], but the feedback suggests that's how it landed. What do you think about that gap?"

**Prioritize (Final 1-2 minutes):**
- Identify what matters most: "Of all these themes, which ones feel most important to address?" "Which would have the biggest impact if you changed them?"
- Look for quick wins vs. deeper work: "Are there some behaviors that would be relatively easy to shift? Which ones might require more sustained effort?"
- Connect to their goals: "Which of these themes, if you addressed them, would most help you achieve your career goals?"

## What NOT to Do
- Don't let them dismiss feedback as "wrong" or "unfair" without exploring it
- Don't agree with dismissals ("Yeah, they probably just don't understand you")
- Don't overwhelm them with too much at once—focus on 2-3 key themes
- Don't let them make it about character ("I'm just a bad communicator") vs. behavior ("I need to work on checking for understanding")

## Key Phrases to Use
- "What patterns do you notice?"
- "How might others be experiencing that behavior?"
- "What do you think they're seeing that led to this feedback?"
- "Let's separate the behavior from who you are as a person..."
- "If you were in their shoes, how might you see this?"
- "What's the gap between your intent and the impact?"

## Coaching Techniques
- **Perspective-taking**: Help them see through others' eyes
- **Pattern recognition**: Connect dots across multiple feedback sources
- **Behavior focus**: Keep it about actions, not character
- **Curiosity over judgment**: "I wonder..." "What if..."
- **Reality testing**: "Does that feedback match anything you've noticed yourself?"

## Transition Signal
When they:
- Demonstrate clear understanding of key themes
- Can articulate the feedback without defensiveness
- Show curiosity about changing behaviors
- Ask "So what should I do about this?"

Then you can suggest: "It sounds like you have a clearer picture of the feedback now. Should we start thinking about what you want to do with these insights?"

This phase is about clarity and understanding, not yet about action. Make sure they truly understand before moving to coaching.
"""
    
    def _get_coaching_prompt(self) -> str:
        """Get coaching for change phase prompt."""
        feedback_summary = self._get_feedback_summary()
        content_themes = self._get_content_themes_summary()
        
        return f"""You are in the COACHING FOR CHANGE phase of the R2C2 framework.

## Phase Goal
Help the employee create a concrete, actionable development plan. This is where insights become action. Focus on 1-3 specific, achievable commitments.

## Feedback Themes
{feedback_summary}

## Key Insights from Our Discussion
{content_themes}

## What to Do

**Prioritize Development Areas (First 1-2 minutes):**
- Narrow the focus: "We've talked about several themes. Which 1-3 areas do you want to focus on first?"
- Check motivation: "Why is this area important to you?" "What would change if you improved here?"
- Ensure ownership: They should choose, not you. "What feels most urgent or impactful to you?"
- Keep it manageable: "Let's not try to change everything at once. What's realistic?"

**Create SMART Goals (Next 2-3 minutes):**
For each priority area, help them create a SMART goal:
- **Specific**: "What exactly will you do differently?" Not "communicate better" but "send a summary email after each meeting"
- **Measurable**: "How will you know you're making progress?" "What would success look like?"
- **Achievable**: "Is this realistic given your current workload and constraints?"
- **Relevant**: "How does this connect to your career goals?" "Why does this matter?"
- **Time-bound**: "When will you start?" "When will you check in on progress?"

**Use START, STOP, CONTINUE Framework:**
- **START**: "What's one new behavior you'll begin doing?"
- **STOP**: "What's one behavior you'll stop or do less of?"
- **CONTINUE**: "What's working that you want to keep doing?"

**Plan for Obstacles (Next 1-2 minutes):**
- Anticipate challenges: "What might get in the way of this change?"
- Problem-solve: "How will you handle it when [obstacle] comes up?"
- Build in support: "Who can help you with this?" "Who will you tell about this commitment?"
- Create accountability: "How will you track your progress?" "When will you check in with yourself?"

**Summarize and Celebrate (Final 1 minute):**
- Recap clearly: "Let me make sure I have this right. You're committing to..."
- Make it concrete: "So starting [when], you'll [specific action]..."
- Acknowledge courage: "This takes real courage. I'm impressed by your commitment to growth."
- Set up follow-up: "When will you review how this is going?" "Who will you share this plan with?"

## What NOT to Do
- Don't let them commit to too much (overwhelming leads to failure)
- Don't accept vague goals ("I'll be better at communication")
- Don't skip the obstacle planning (unrealistic optimism leads to disappointment)
- Don't make it your plan—it has to be theirs
- Don't forget to celebrate their commitment

## Key Phrases to Use
- "What specifically will you do differently?"
- "How will you know you're making progress?"
- "What might get in the way?"
- "Who can support you in this?"
- "Let's make this concrete..."
- "What's one small step you can take this week?"

## SMART Goal Examples
**Vague**: "I'll communicate better"
**SMART**: "I'll send a brief summary email within 24 hours of every stakeholder meeting, highlighting decisions made and next steps"

**Vague**: "I'll delegate more"
**SMART**: "I'll identify one task per week that I can delegate to a team member, and I'll schedule a 15-minute coaching conversation when I hand it off"

**Vague**: "I'll be less defensive"
**SMART**: "When I receive critical feedback, I'll pause for 3 seconds before responding, and I'll ask one clarifying question before defending my position"

## Development Plan Structure
For each goal, capture:
1. **Goal Type**: START / STOP / CONTINUE
2. **Specific Behavior**: Exactly what they'll do
3. **Success Metric**: How they'll measure progress
4. **Timeline**: When they'll start and when they'll review
5. **Support**: Who will help them
6. **Obstacles**: What might get in the way and how they'll handle it

## Transition to Closing
When you have 1-3 concrete commitments:
- Summarize the full plan
- Acknowledge their growth through this conversation
- Remind them this is a journey, not a destination
- Encourage them to be kind to themselves as they practice new behaviors

This is the payoff phase. Make sure they leave with a clear, actionable plan they're genuinely committed to.
"""
    
    def get_phase_guidance(self) -> Dict[str, Any]:
        """Get structured guidance for the current phase.
        
        Returns:
            Dictionary with phase guidance including goals, key questions, and tips
        """
        phase = self.state.current_phase
        
        guidance = {
            'phase': phase.value,
            'time_in_phase': self.get_time_in_phase(),
            'goals': [],
            'key_questions': [],
            'tips': []
        }
        
        if phase == R2C2Phase.RELATIONSHIP:
            guidance['goals'] = [
                'Build rapport and trust',
                'Create psychological safety',
                'Set expectations for the conversation'
            ]
            guidance['key_questions'] = [
                'How are you feeling about the feedback you received?',
                'What was it like to read through your 360° feedback?',
                'Have you received feedback like this before?'
            ]
            guidance['tips'] = [
                'Be warm and empathetic',
                'Validate their feelings',
                'Keep it brief (2-3 minutes)'
            ]
        
        elif phase == R2C2Phase.REACTION:
            guidance['goals'] = [
                'Explore emotional reactions',
                'Normalize defensiveness',
                'Reduce emotional barriers to learning'
            ]
            guidance['key_questions'] = [
                'What was your first reaction when you read the feedback?',
                'Which pieces of feedback surprised you or felt unfair?',
                'What emotions are coming up as we talk about this?'
            ]
            guidance['tips'] = [
                'Don\'t rush this phase',
                'Reflect emotions back',
                'Avoid problem-solving yet'
            ]
        
        elif phase == R2C2Phase.CONTENT:
            guidance['goals'] = [
                'Understand feedback objectively',
                'Identify patterns and themes',
                'Distinguish behavior from identity'
            ]
            guidance['key_questions'] = [
                'What patterns do you notice across the feedback?',
                'How might others be experiencing your behavior?',
                'Which feedback themes feel most important to address?'
            ]
            guidance['tips'] = [
                'Help them see others\' perspectives',
                'Focus on behaviors, not character',
                'Look for recurring themes'
            ]
        
        elif phase == R2C2Phase.COACHING:
            guidance['goals'] = [
                'Create actionable development plan',
                'Set SMART goals',
                'Identify specific behavior changes'
            ]
            guidance['key_questions'] = [
                'What 1-3 areas do you want to focus on?',
                'What specific behavior will you start/stop/continue?',
                'What obstacles might you face?',
                'Who can support you in this change?'
            ]
            guidance['tips'] = [
                'Keep it focused (1-3 goals)',
                'Make goals specific and measurable',
                'Ensure commitments are realistic'
            ]
        
        return guidance
    
    def _get_feedback_summary(self) -> str:
        """Generate a summary of feedback themes."""
        if not self.state.feedback_data.themes:
            return "No specific feedback themes provided yet."
        
        summary_lines = []
        for theme in self.state.feedback_data.themes[:5]:  # Top 5 themes
            category = theme.get('category', 'general')
            theme_text = theme.get('theme', '')
            frequency = theme.get('frequency', 0)
            
            summary_lines.append(f"- [{category.upper()}] {theme_text} (mentioned {frequency} times)")
        
        return "\n".join(summary_lines) if summary_lines else "General 360° feedback provided."
    
    def _get_reactions_summary(self) -> str:
        """Generate a summary of user reactions."""
        if not self.state.user_reactions:
            return "No reactions recorded yet."
        
        # Get last 3 reactions
        recent_reactions = self.state.user_reactions[-3:]
        return "\n".join(f"- {reaction}" for reaction in recent_reactions)
    
    def _get_content_themes_summary(self) -> str:
        """Generate a summary of content themes discussed."""
        if not self.state.content_themes:
            return "No content themes discussed yet."
        
        return "\n".join(f"- {theme}" for theme in self.state.content_themes)

    
    def record_user_response(
        self, 
        response: str, 
        emotion: Optional[EmotionState] = None
    ) -> None:
        """Record a user response and update conversation state.
        
        Args:
            response: The user's text response
            emotion: Optional emotion state detected during response
        """
        # Add emotion to history if provided
        if emotion:
            self.state.emotional_states.append(emotion)
        
        # Track responses based on current phase
        phase = self.state.current_phase
        
        if phase == R2C2Phase.REACTION:
            # Record emotional reactions
            self.state.user_reactions.append(response)
        
        elif phase == R2C2Phase.CONTENT:
            # Extract and record content themes being discussed
            # Simple keyword-based extraction for MVP
            self._extract_content_themes(response)
        
        elif phase == R2C2Phase.COACHING:
            # Extract development plan items
            self._extract_development_items(response)
    
    def _extract_content_themes(self, response: str) -> None:
        """Extract content themes from user response.
        
        Args:
            response: User's response text
        """
        # Simple keyword matching for MVP
        # In production, this could use NLP for better extraction
        keywords = [
            'communication', 'leadership', 'collaboration', 'feedback',
            'delegation', 'listening', 'empathy', 'decision-making',
            'accountability', 'follow-through', 'organization', 'planning'
        ]
        
        response_lower = response.lower()
        for keyword in keywords:
            if keyword in response_lower and keyword not in self.state.content_themes:
                self.state.content_themes.append(keyword)
    
    def _extract_development_items(self, response: str) -> None:
        """Extract development plan items from user response.
        
        Args:
            response: User's response text
        """
        # Initialize development plan if needed
        if self.state.development_plan is None:
            self.state.development_plan = DevelopmentPlan(
                created_at=datetime.now()
            )
        
        # Simple extraction for MVP - look for action words
        response_lower = response.lower()
        
        # Detect goal type
        goal_type = None
        if any(word in response_lower for word in ['start', 'begin', 'initiate']):
            goal_type = 'start'
        elif any(word in response_lower for word in ['stop', 'quit', 'cease', 'avoid']):
            goal_type = 'stop'
        elif any(word in response_lower for word in ['continue', 'keep', 'maintain']):
            goal_type = 'continue'
        
        # If we detected a goal, add it
        if goal_type and len(response) > 20:  # Meaningful response
            goal = {
                'type': goal_type,
                'description': response,
                'timestamp': datetime.now().isoformat()
            }
            self.state.development_plan.goals.append(goal)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive session summary.
        
        Returns:
            Dictionary containing session summary data
        """
        session_duration = (datetime.now() - self._session_start_time).total_seconds()
        
        # Calculate phase durations
        phase_durations = {}
        for phase_record in self.state.phase_history:
            phase_name = phase_record['phase']
            duration = phase_record['duration']
            phase_durations[phase_name] = duration
        
        # Add current phase duration
        current_phase_duration = self.get_time_in_phase()
        phase_durations[self.state.current_phase.value] = current_phase_duration
        
        # Analyze emotional journey
        emotional_journey = self._analyze_emotional_journey()
        
        # Compile summary
        summary = {
            'session_id': None,  # Will be set by database layer
            'user_id': self.state.feedback_data.user_id,
            'start_time': self._session_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': session_duration,
            'phase_durations': phase_durations,
            'phases_completed': [p['phase'] for p in self.state.phase_history],
            'current_phase': self.state.current_phase.value,
            'emotional_journey': emotional_journey,
            'reactions_explored': len(self.state.user_reactions),
            'content_themes_discussed': self.state.content_themes,
            'development_plan': self._format_development_plan(),
            'key_insights': self._generate_key_insights(),
        }
        
        return summary
    
    def _analyze_emotional_journey(self) -> Dict[str, Any]:
        """Analyze the emotional journey throughout the session.
        
        Returns:
            Dictionary with emotional journey analysis
        """
        if not self.state.emotional_states:
            return {
                'start_emotion': 'unknown',
                'end_emotion': 'unknown',
                'predominant_emotion': 'unknown',
                'emotion_changes': 0
            }
        
        emotions = self.state.emotional_states
        
        # Count emotion frequencies
        emotion_counts = {}
        for emotion_state in emotions:
            emotion = emotion_state.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Find predominant emotion
        predominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'unknown'
        
        # Count emotion changes
        emotion_changes = 0
        for i in range(1, len(emotions)):
            if emotions[i].emotion != emotions[i-1].emotion:
                emotion_changes += 1
        
        return {
            'start_emotion': emotions[0].emotion if emotions else 'unknown',
            'end_emotion': emotions[-1].emotion if emotions else 'unknown',
            'predominant_emotion': predominant_emotion,
            'emotion_changes': emotion_changes,
            'emotion_distribution': emotion_counts
        }
    
    def _format_development_plan(self) -> Dict[str, Any]:
        """Format the development plan for summary.
        
        Returns:
            Formatted development plan dictionary
        """
        if not self.state.development_plan:
            return {
                'goals': [],
                'created': False
            }
        
        return {
            'goals': self.state.development_plan.goals,
            'goal_count': len(self.state.development_plan.goals),
            'created': True,
            'created_at': self.state.development_plan.created_at.isoformat() if self.state.development_plan.created_at else None
        }
    
    def _generate_key_insights(self) -> List[str]:
        """Generate key insights from the session.
        
        Returns:
            List of key insight strings
        """
        insights = []
        
        # Insight about emotional journey
        if self.state.emotional_states:
            emotions = self.state.emotional_states
            if emotions[0].emotion in self.DEFENSIVE_EMOTIONS and emotions[-1].emotion in self.READY_EMOTIONS:
                insights.append("Successfully processed initial defensiveness and reached a receptive state")
        
        # Insight about content themes
        if len(self.state.content_themes) >= 3:
            insights.append(f"Identified {len(self.state.content_themes)} key development themes")
        
        # Insight about development plan
        if self.state.development_plan and len(self.state.development_plan.goals) > 0:
            goal_count = len(self.state.development_plan.goals)
            insights.append(f"Created development plan with {goal_count} actionable goal(s)")
        
        # Insight about phase completion
        if len(self.state.phase_history) >= 3:
            insights.append("Completed full R2C2 framework journey")
        
        return insights if insights else ["Session in progress"]
    
    def get_state(self) -> R2C2State:
        """Get the current R2C2 state.
        
        Returns:
            Current state object
        """
        return self.state
    
    def restore_state(self, state: R2C2State) -> None:
        """Restore a previous R2C2 state.
        
        Args:
            state: State object to restore
        """
        self.state = state
