import os
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

class QuizService:
    """Service for managing phishing awareness quizzes."""
    
    def __init__(self):
        """Initialize the quiz service."""
        # Ensure templates directory exists
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Path to quiz questions file
        self.quiz_file = self.templates_dir / "quiz_questions.json"
        
        # Load quiz questions
        self.questions = self._load_questions()
    
    def _load_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load quiz questions from file."""
        if not self.quiz_file.exists():
            # Create default quiz questions
            default_questions = {
                "phishing_indicators": [
                    {
                        "id": "sender_mismatch",
                        "question": "What was suspicious about the sender of the email?",
                        "options": [
                            "The display name didn't match the email address",
                            "The domain was misspelled (e.g., microsoftt.com)",
                            "The email came from a free email provider (gmail, yahoo, etc.)",
                            "The sender used an unusual format (e.g., no-reply@)"
                        ],
                        "correct_answer": 0,
                        "explanation": "Always check that the sender's email address matches what you expect, not just the display name which can be easily spoofed."
                    },
                    {
                        "id": "urgency",
                        "question": "What psychological tactic did this email use?",
                        "options": [
                            "Urgency - claiming immediate action was required",
                            "Authority - impersonating a person of power",
                            "Scarcity - offering a limited-time opportunity",
                            "Curiosity - enticing you to learn more"
                        ],
                        "correct_answer": 0,
                        "explanation": "Phishing emails often create a false sense of urgency to prevent you from thinking critically about the request."
                    },
                    {
                        "id": "generic_greeting",
                        "question": "What was suspicious about how the email addressed you?",
                        "options": [
                            "It used a generic greeting (Dear User, Customer, etc.)",
                            "It addressed me by my email instead of my name",
                            "It used my name but misspelled it",
                            "It didn't include any greeting at all"
                        ],
                        "correct_answer": 0,
                        "explanation": "Legitimate organizations that have your information typically address you by name, not with generic terms."
                    },
                    {
                        "id": "suspicious_link",
                        "question": "What was suspicious about the link in the email?",
                        "options": [
                            "The URL didn't match the organization it claimed to be from",
                            "Hovering over the link showed a different destination than the text",
                            "The link used URL shortening services to hide the real destination",
                            "The link contained unusual characters or numbers"
                        ],
                        "correct_answer": 1,
                        "explanation": "Always hover over links before clicking to see the actual destination URL, which often reveals phishing attempts."
                    },
                    {
                        "id": "poor_formatting",
                        "question": "What visual clue suggested this was a phishing email?",
                        "options": [
                            "Poor grammar or spelling errors",
                            "Inconsistent formatting or fonts",
                            "Low-quality or missing company logo",
                            "Unusual email layout compared to legitimate emails"
                        ],
                        "correct_answer": 0,
                        "explanation": "Legitimate organizations typically have professional communications without basic grammar or spelling mistakes."
                    }
                ],
                "best_practices": [
                    {
                        "id": "next_steps",
                        "question": "What should you do if you suspect an email is a phishing attempt?",
                        "options": [
                            "Report it to your IT security team",
                            "Forward it to colleagues to get their opinion",
                            "Reply to the sender to confirm if it's legitimate",
                            "Delete it immediately without reporting it"
                        ],
                        "correct_answer": 0,
                        "explanation": "Always report suspected phishing to your security team so they can investigate and alert others if necessary."
                    },
                    {
                        "id": "clicked_link",
                        "question": "What should you do if you've already clicked a suspicious link?",
                        "options": [
                            "Immediately notify IT security and change your passwords",
                            "Wait to see if anything unusual happens to your account",
                            "Only report it if you entered sensitive information",
                            "Run an antivirus scan and consider the issue resolved"
                        ],
                        "correct_answer": 0,
                        "explanation": "Quick reporting allows security teams to mitigate potential damage, even if you didn't enter credentials."
                    },
                    {
                        "id": "verify_requests",
                        "question": "What's the best way to verify a suspicious request for sensitive information?",
                        "options": [
                            "Contact the sender through a known, official channel (not by replying)",
                            "Check if the email has a digital signature",
                            "Look for the organization's official logo in the email",
                            "Check if the email was sent during business hours"
                        ],
                        "correct_answer": 0,
                        "explanation": "Always verify requests through official channels you initiate yourself, like calling the company's official phone number."
                    }
                ]
            }
            
            # Save default questions
            with open(self.quiz_file, 'w') as f:
                json.dump(default_questions, f, indent=2)
            
            return default_questions
        
        try:
            with open(self.quiz_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading quiz questions: {e}")
            return {}
    
    def generate_quiz(self, difficulty: int = 2, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate a quiz with a selection of questions.
        
        Args:
            difficulty: The difficulty level (1-3) with higher being more questions
            categories: Optional list of question categories to include
            
        Returns:
            A list of quiz questions
        """
        # Determine number of questions based on difficulty
        num_questions = {
            1: 2,  # Easy: 2 questions
            2: 3,  # Medium: 3 questions
            3: 5   # Hard: 5 questions
        }.get(difficulty, 3)
        
        # Use specified categories or all available
        if categories:
            question_pool = []
            for category in categories:
                if category in self.questions:
                    question_pool.extend(self.questions[category])
        else:
            question_pool = [q for category in self.questions.values() for q in category]
        
        # Ensure we don't try to select more questions than available
        num_questions = min(num_questions, len(question_pool))
        
        # Randomly select questions
        selected_questions = random.sample(question_pool, num_questions)
        
        # Format questions for the quiz (remove correct answer and explanation)
        quiz_questions = []
        for question in selected_questions:
            quiz_question = {
                "id": question["id"],
                "question": question["question"],
                "options": question["options"]
            }
            quiz_questions.append(quiz_question)
        
        return quiz_questions
    
    def grade_quiz(self, answers: Dict[str, int]) -> Dict[str, Any]:
        """Grade a completed quiz.
        
        Args:
            answers: Dictionary mapping question IDs to selected answer indices
            
        Returns:
            A dictionary with quiz results
        """
        total_questions = len(answers)
        correct_answers = 0
        question_results = []
        
        # Flatten all questions for easier lookup
        all_questions = {}
        for category in self.questions.values():
            for question in category:
                all_questions[question["id"]] = question
        
        # Grade each answer
        for question_id, selected_answer in answers.items():
            if question_id in all_questions:
                question = all_questions[question_id]
                is_correct = selected_answer == question["correct_answer"]
                
                if is_correct:
                    correct_answers += 1
                
                question_results.append({
                    "id": question_id,
                    "question": question["question"],
                    "selected_answer": selected_answer,
                    "correct_answer": question["correct_answer"],
                    "is_correct": is_correct,
                    "explanation": question["explanation"]
                })
        
        # Calculate score as percentage
        score_percent = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score_percent": score_percent,
            "question_results": question_results
        }
    
    def get_educational_content(self, scenario_type: str) -> Dict[str, str]:
        """Get educational content about phishing based on the scenario type.
        
        Args:
            scenario_type: The type of phishing scenario
            
        Returns:
            A dictionary with educational content
        """
        # Basic educational content for all scenarios
        content = {
            "title": "Phishing Awareness: What You Should Know",
            "intro": "You just participated in a simulated phishing exercise. This was a safe test designed to help you recognize and respond appropriately to real phishing attempts.",
            "what_is_phishing": "Phishing is a type of social engineering attack where attackers impersonate trusted entities to trick victims into revealing sensitive information or taking harmful actions like clicking malicious links.",
            "common_indicators": [
                "Sender email address doesn't match the claimed identity",
                "Urgent or threatening language to create pressure",
                "Generic greetings instead of your name",
                "Requests for sensitive information",
                "Poor grammar or spelling errors",
                "Suspicious links or attachments"
            ],
            "best_practices": [
                "Verify requests through official channels",
                "Hover over links before clicking to see the actual URL",
                "Never provide sensitive information in response to an email",
                "Report suspicious emails to your IT security team",
                "Keep software and security awareness updated"
            ]
        }
        
        # Add scenario-specific content
        scenario_content = {
            "credential-theft": {
                "scenario_title": "Account Credential Phishing",
                "scenario_description": "This simulation mimicked attempts to steal your login credentials by creating a sense of urgency about your account security.",
                "specific_tips": [
                    "Legitimate organizations will never ask for your password via email",
                    "Access accounts by typing the URL directly in your browser, not by clicking email links",
                    "Enable two-factor authentication for additional security"
                ]
            },
            "invoice": {
                "scenario_title": "Invoice or Payment Fraud",
                "scenario_description": "This simulation mimicked attempts to trick you into paying fake invoices or revealing financial information.",
                "specific_tips": [
                    "Verify all payment requests through established financial processes",
                    "Check for subtle changes in vendor payment details",
                    "Be wary of unexpected invoices or changes to payment procedures"
                ]
            },
            "oauth-consent": {
                "scenario_title": "OAuth Consent Phishing",
                "scenario_description": "This simulation mimicked attempts to trick you into granting permissions to malicious applications.",
                "specific_tips": [
                    "Carefully review all permission requests before approving",
                    "Verify the application developer is legitimate",
                    "Only grant the minimum permissions necessary"
                ]
            },
            "shipping": {
                "scenario_title": "Shipping Notification Phishing",
                "scenario_description": "This simulation mimicked fake shipping notifications designed to create curiosity about a package.",
                "specific_tips": [
                    "Track packages directly through the shipper's official website",
                    "Be suspicious of unexpected delivery notifications",
                    "Check the tracking number format matches the claimed shipper"
                ]
            }
        }
        
        # Normalize scenario type
        normalized_scenario = scenario_type.lower().replace("/", "-").replace(" ", "-")
        
        # Add scenario-specific content if available
        if normalized_scenario in scenario_content:
            content.update(scenario_content[normalized_scenario])
        else:
            # Generic scenario content
            content.update({
                "scenario_title": "Phishing Simulation",
                "scenario_description": "This simulation demonstrated common phishing tactics used by attackers.",
                "specific_tips": [
                    "Always verify unexpected communications before taking action",
                    "When in doubt, contact the sender through official channels",
                    "Trust your instincts if something feels suspicious"
                ]
            })
        
        return content