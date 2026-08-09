import os
import google.generativeai as genai
from typing import Dict, List, Optional
from models.schemas import InterviewState
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY not found in .env file")
    print("Please add: GOOGLE_API_KEY=your-key-here to .env")
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE"  # Fallback

genai.configure(api_key=GOOGLE_API_KEY)

class AIIntegration:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.question_count = 0
        self.max_questions = 8
        self.covered_days = set()  # Track which days are covered
        self.all_curriculum_days = self._load_curriculum_days()
    
    def _load_curriculum_days(self) -> Dict[int, Dict]:
        """Load curriculum days from the JSON file"""
        try:
            import json
            from pathlib import Path
            
            # Try to find curriculum.json
            data_path = Path(__file__).parent.parent / "data" / "curriculum.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    curriculum = json.load(f)
                    days = {}
                    for day_data in curriculum.get('days', []):
                        day_num = day_data.get('day')
                        if day_num:
                            days[day_num] = {
                                'title': day_data.get('title', ''),
                                'objectives': day_data.get('objectives', []),
                                'tools': day_data.get('tools', [])
                            }
                    return days
        except Exception as e:
            print(f"Error loading curriculum: {e}")
        
        # Fallback: return empty dict
        return {}
    
    def _get_day_details(self, day_number: int) -> Optional[Dict]:
        """Get details for a specific day"""
        return self.all_curriculum_days.get(day_number)
    
    def _select_curriculum_day(self, candidate_data: Dict, used_days: set) -> Optional[int]:
        """
        Select a curriculum day for the next question.
        Ensures diversity by avoiding used days.
        """
        # Get all days the candidate completed
        completed_days = []
        for mission in candidate_data.get('missions', []):
            if mission.get('passed', False) and not mission.get('skipped', False):
                day = mission.get('day')
                if day:
                    completed_days.append(day)
        
        # If candidate has no completed days, use day 7 as default
        if not completed_days:
            return 7
        
        # Filter out already used days
        available_days = [d for d in completed_days if d not in used_days]
        
        # If all days are used, pick a random one from completed
        if not available_days:
            # Prefer days 7, 8, 10, 12, 16, 22, 28, 31 (core topics)
            prioritized = [7, 8, 10, 12, 16, 22, 28, 31]
            for day in prioritized:
                if day in completed_days:
                    return day
            return completed_days[0]
        
        # Prioritize days that haven't been used
        # Prioritize core days
        prioritized = [7, 8, 10, 12, 16, 22, 28, 31]
        for day in prioritized:
            if day in available_days:
                return day
        
        # Return first available day
        return available_days[0]
    
    def _get_question_prompt(self, day_number: int, candidate_data: Dict, 
                            is_follow_up: bool = False, 
                            previous_answer: str = None,
                            conversation_history: str = None) -> str:
        """
        Generate a prompt for the AI based on the selected day.
        """
        day_details = self._get_day_details(day_number)
        day_title = day_details.get('title', 'Unknown Topic') if day_details else 'Unknown Topic'
        objectives = day_details.get('objectives', []) if day_details else []
        tools = day_details.get('tools', []) if day_details else []
        
        # Get all completed missions
        missions = candidate_data.get('missions', [])
        completed = [m for m in missions if m.get('passed', False)]
        skipped = [m for m in missions if m.get('skipped', False)]
        failed = [m for m in missions if not m.get('passed', False) and not m.get('skipped', False)]
        
        candidate_name = candidate_data.get('member', {}).get('name', 'Candidate')
        job_role = candidate_data.get('member', {}).get('jobRole', 'Engineer')
        experience = candidate_data.get('member', {}).get('yearsExperience', 0)
        
        # Build context about candidate's performance
        performance_context = ""
        if completed:
            completed_titles = [m.get('title', '') for m in completed[:3]]
            performance_context += f"Completed with {len(completed)} missions passed. "
            
            # Check for first-try passes (strong signals)
            first_try_missions = [m for m in completed if m.get('attempts', 0) == 1]
            if first_try_missions:
                performance_context += f"Completed {len(first_try_missions)} missions on first try. "
        
        if skipped:
            skipped_titles = [m.get('title', '') for m in skipped[:2]]
            performance_context += f"Note: Candidate skipped {len(skipped)} topics including: {', '.join(skipped_titles)}. "
        
        if failed:
            failed_titles = [m.get('title', '') for m in failed[:2]]
            performance_context += f"Note: Candidate struggled with {len(failed)} topics including: {', '.join(failed_titles)}. "
        
        # Build the prompt
        if is_follow_up:
            base_prompt = f"""
You are a professional technical interviewer for an AI engineering program. You're conducting a personalized interview with a candidate.

**Candidate:** {candidate_name}
**Job Role:** {job_role}
**Experience:** {experience} years
**Performance:** {performance_context}

**Current Topic:** Day {day_number} - {day_title}
**Learning Objectives:** {', '.join(objectives) if objectives else 'General understanding'}
**Tools Used:** {', '.join(tools) if tools else 'Various AI tools'}

**Conversation History:**
{conversation_history}

**Candidate's Latest Answer:** {previous_answer}

Generate a NATURAL follow-up question about this topic.

Guidelines:
- Reference the specific day: "On Day {day_number}, you learned about {day_title}..."
- If the answer was good → ask a deeper, more challenging question
- If the answer was vague → ask for clarification with specific examples
- If they struggled → ask a simpler question or explain the concept
- Make it conversational, not robotic
- Keep it to 2-3 sentences
- Always reference the curriculum day number so we can track coverage
"""
        else:
            base_prompt = f"""
You are a professional technical interviewer for an AI engineering program. You're conducting a personalized interview with a candidate.

**Candidate:** {candidate_name}
**Job Role:** {job_role}
**Experience:** {experience} years
**Performance:** {performance_context}

**Topic for this question:** Day {day_number} - {day_title}
**Learning Objectives:** {', '.join(objectives) if objectives else 'General understanding'}
**Tools Used:** {', '.join(tools) if tools else 'Various AI tools'}

Generate a WELCOME message and the FIRST technical question about this topic.

Guidelines:
- Start with a warm welcome
- Reference the specific day: "On Day {day_number}, you learned about {day_title}..."
- Make it specific to their learning journey
- The question should test their understanding, not just memory
- Reference their job role and experience level
- Keep it to 3-4 sentences total
"""
        
        return base_prompt
    
    def initialize_interview(self, candidate_data: Dict, session_id: str) -> Dict:
        """Generate first question"""
        
        self.question_count = 0
        self.covered_days = set()
        
        # Select first curriculum day
        first_day = self._select_curriculum_day(candidate_data, set())
        self.covered_days.add(first_day)
        
        # Generate prompt
        prompt = self._get_question_prompt(
            day_number=first_day,
            candidate_data=candidate_data,
            is_follow_up=False
        )
        
        try:
            response = self.model.generate_content(prompt)
            reply = response.text
            self.question_count = 1
            
            # Ensure day reference is in the reply
            if f"Day {first_day}" not in reply:
                # Add a reference if missing
                day_details = self._get_day_details(first_day)
                title = day_details.get('title', 'this topic') if day_details else 'this topic'
                reply = f"Welcome! On Day {first_day}, you learned about {title}. " + reply
            
        except Exception as e:
            print(f"AI Error: {e}")
            day_details = self._get_day_details(first_day)
            title = day_details.get('title', 'embeddings') if day_details else 'embeddings'
            reply = f"Welcome {candidate_data.get('member', {}).get('name', 'Candidate')}! On Day {first_day}, you learned about {title}. Can you explain what you learned and why it's important for AI applications?"
            self.question_count = 1
        
        return {
            "reply": reply,
            "done": False,
            "day_covered": first_day
        }
    
    def process_message(self, state: InterviewState, message: str) -> Dict:
        """Process user response and generate follow-up"""
        
        self.question_count += 1
        
        # Check if we should end
        if self.question_count > self.max_questions:
            return {
                "reply": "Thank you for your answers! That concludes our interview. I'll provide your feedback shortly.",
                "done": True
            }
        
        # Get conversation history
        history = ""
        for i in range(min(len(state.questions_asked), len(state.answers))):
            q = state.questions_asked[i]
            a = state.answers[i] if i < len(state.answers) else {}
            history += f"AI: {q.question}\n"
            history += f"Candidate: {a.get('answer', '')}\n"
        
        # Get candidate data from state
        candidate_data = state.candidate_data
        
        # Select next curriculum day (avoid used days)
        next_day = self._select_curriculum_day(candidate_data, self.covered_days)
        self.covered_days.add(next_day)
        
        # Generate prompt for follow-up
        prompt = self._get_question_prompt(
            day_number=next_day,
            candidate_data=candidate_data,
            is_follow_up=True,
            previous_answer=message,
            conversation_history=history
        )
        
        try:
            response = self.model.generate_content(prompt)
            reply = response.text
            
            # Ensure day reference is in the reply
            if f"Day {next_day}" not in reply:
                day_details = self._get_day_details(next_day)
                title = day_details.get('title', 'this topic') if day_details else 'this topic'
                # Prepend day reference if missing
                reply = f"Let's move on to Day {next_day} where you covered {title}. " + reply
            
        except Exception as e:
            print(f"AI Error: {e}")
            day_details = self._get_day_details(next_day)
            title = day_details.get('title', 'AI concepts') if day_details else 'AI concepts'
            
            # Fallback questions based on day
            fallback_questions = {
                7: f"On Day {next_day}, you learned about embeddings. Can you explain what embeddings are and how they're used in vector search?",
                8: f"On Day {next_day}, you covered vector databases. Can you compare vector databases with traditional relational databases?",
                10: f"On Day {next_day}, you built a retrieval engine. How would you design a hybrid retrieval system that combines keyword and vector search?",
                12: f"On Day {next_day}, you studied prompt engineering. What are some techniques you've found effective for improving LLM responses?",
                16: f"On Day {next_day}, you built a chatbot backend. How would you design the API for a production chatbot?",
                22: f"On Day {next_day}, you worked with multi-agent systems. What's your approach to orchestrating multiple AI agents?",
                28: f"On Day {next_day}, you deployed AI systems. Walk me through your Docker and Kubernetes deployment strategy.",
            }
            reply = fallback_questions.get(next_day, f"On Day {next_day}, you learned about {title}. Can you share your key takeaways from this topic?")
        
        return {
            "reply": reply,
            "done": False,
            "day_covered": next_day
        }
    
    def generate_feedback(self, state: InterviewState) -> Dict:
        """Generate final feedback with day coverage info"""
        
        # Get covered days from state or from tracked set
        covered_days = self.covered_days
        if not covered_days:
            # Try to extract from questions
            for q in state.questions_asked:
                match = re.search(r'Day\s*(\d+)', q.question)
                if match:
                    covered_days.add(int(match.group(1)))
        
        covered_days_list = sorted(list(covered_days))
        covered_days_text = ', '.join([f"Day {d}" for d in covered_days_list]) if covered_days_list else "No specific days"
        
        # Build transcript
        transcript = ""
        for i in range(min(len(state.questions_asked), len(state.answers))):
            q = state.questions_asked[i]
            a = state.answers[i] if i < len(state.answers) else {}
            transcript += f"Q: {q.question}\n"
            transcript += f"A: {a.get('answer', '')}\n\n"
        
        # Get candidate info
        candidate_data = state.candidate_data
        candidate_name = candidate_data.get('member', {}).get('name', 'Candidate')
        job_role = candidate_data.get('member', {}).get('jobRole', 'Engineer')
        
        prompt = f"""
Analyze this interview conversation and provide structured feedback.

**Candidate:** {candidate_name}
**Job Role:** {job_role}
**Questions Asked:** {len(state.questions_asked)}
**Curriculum Days Covered:** {covered_days_text}

**Interview transcript:**
{transcript}

Provide feedback in this exact format:

SUMMARY: [Overall performance summary - 2-3 sentences, mention their knowledge of covered days]

STRENGTHS:
- [Strength 1 - specific to their knowledge]
- [Strength 2 - specific to their communication]
- [Strength 3 - specific to their problem-solving]

GAPS:
- [Gap 1 - specific topic they need to improve]
- [Gap 2 - specific skill they need to develop]
- [Gap 3 - specific area for growth]

NEXT STEPS:
- [Recommendation 1 - based on their gaps]
- [Recommendation 2 - based on their job role]
- [Recommendation 3 - based on the curriculum days covered]

Be specific, constructive, and actionable. Reference specific days and topics from the interview.
"""
        
        try:
            response = self.model.generate_content(prompt)
            feedback_text = response.text
            
            # Parse the feedback
            summary = ""
            strengths = []
            gaps = []
            next_steps = []
            
            lines = feedback_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('STRENGTHS:'):
                    current_section = 'strengths'
                elif line.startswith('GAPS:'):
                    current_section = 'gaps'
                elif line.startswith('NEXT STEPS:'):
                    current_section = 'next'
                elif line.startswith('-') and current_section == 'strengths':
                    strengths.append(line.replace('-', '').strip())
                elif line.startswith('-') and current_section == 'gaps':
                    gaps.append(line.replace('-', '').strip())
                elif line.startswith('-') and current_section == 'next':
                    next_steps.append(line.replace('-', '').strip())
            
            # If parsing failed, use defaults with day info
            if not summary:
                summary = f"The candidate demonstrated knowledge across {len(covered_days_list)} curriculum days including {covered_days_text}."
            if not strengths:
                strengths = ["Good understanding of core AI concepts", "Clear communication", "Able to connect theory to practice"]
            if not gaps:
                gaps = ["Could explore advanced topics more deeply", "More practical examples would strengthen responses"]
            if not next_steps:
                next_steps = [
                    f"Review Day {d} topics in more depth" for d in covered_days_list[:3]
                ] if covered_days_list else ["Review all AI curriculum topics", "Practice system design interviews"]
            
        except Exception as e:
            print(f"AI Error in feedback: {e}")
            summary = f"The candidate showed understanding of AI concepts across {len(covered_days_list)} curriculum days."
            strengths = ["Technical knowledge", "Communication skills", "Learning ability"]
            gaps = ["Could go deeper on some topics", "More specific examples would help"]
            next_steps = ["Practice more interview questions", "Review advanced AI topics", "Build more projects"]
        
        # Ensure we have at least 3 items in each list
        while len(strengths) < 3:
            strengths.append("Demonstrated interest in AI")
        while len(gaps) < 3:
            gaps.append("Continue learning advanced topics")
        while len(next_steps) < 3:
            next_steps.append("Review curriculum materials")
        
        return {
            "summary": summary,
            "strengths": strengths[:3],
            "gaps": gaps[:3],
            "next": next_steps[:3]
        }