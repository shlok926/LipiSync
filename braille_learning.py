# braille_learning.py — Interactive Braille learning module with flashcards & quizzes

import random
from typing import List, Dict
from enum import Enum

class DifficultyLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3

class BrailleLesson:
    """Represents a single lesson in Braille."""
    
    def __init__(self, lesson_id: int, title: str, description: str, 
                 braille_chars: Dict[str, str], difficulty: DifficultyLevel):
        self.id = lesson_id
        self.title = title
        self.description = description
        self.braille_chars = braille_chars  # {'a': '⠁', 'b': '⠃', ...}
        self.difficulty = difficulty
    
    def get_char_count(self) -> int:
        return len(self.braille_chars)

class BrailleFlashcard:
    """A single flashcard for learning Braille."""
    
    def __init__(self, front: str, back: str, card_type: str = 'text_to_braille'):
        self.front = front  # What the user sees first
        self.back = back    # The answer
        self.card_type = card_type  # 'text_to_braille' or 'braille_to_text'
        self.attempts = 0
        self.correct_count = 0
    
    def mark_correct(self):
        self.attempts += 1
        self.correct_count += 1
    
    def mark_incorrect(self):
        self.attempts += 1
    
    def get_accuracy(self) -> float:
        if self.attempts == 0:
            return 0.0
        return (self.correct_count / self.attempts) * 100

class BrailleQuiz:
    """Interactive quiz for testing Braille knowledge."""
    
    def __init__(self, lesson: BrailleLesson, num_questions: int = 10):
        self.lesson = lesson
        self.num_questions = num_questions
        self.current_question = 0
        self.correct_answers = 0
        self.questions = self._generate_questions()
    
    def _generate_questions(self) -> List[Dict]:
        """Generate quiz questions from lesson content."""
        questions = []
        items = list(self.lesson.braille_chars.items())
        
        for _ in range(min(self.num_questions, len(items))):
            # Random question type
            question_type = random.choice(['text_to_braille', 'braille_to_text'])
            
            # Random char
            text_char, braille_char = random.choice(items)
            
            if question_type == 'text_to_braille':
                questions.append({
                    'type': 'text_to_braille',
                    'question': f"What is '{text_char}' in Braille?",
                    'correct_answer': braille_char,
                    'shown': text_char,
                })
            else:
                questions.append({
                    'type': 'braille_to_text',
                    'question': f"What character is '{braille_char}'?",
                    'correct_answer': text_char,
                    'shown': braille_char,
                })
        
        random.shuffle(questions)
        return questions
    
    def get_current_question(self) -> Dict:
        """Get the current question."""
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return {}
    
    def check_answer(self, user_answer: str) -> bool:
        """Check if answer is correct and advance."""
        if self.current_question >= len(self.questions):
            return False
        
        current = self.questions[self.current_question]
        is_correct = user_answer.strip().lower() == current['correct_answer'].strip().lower()
        
        if is_correct:
            self.correct_answers += 1
        
        self.current_question += 1
        return is_correct
    
    def get_score(self) -> float:
        """Get current score percentage."""
        if self.current_question == 0:
            return 0.0
        return (self.correct_answers / self.current_question) * 100
    
    def is_complete(self) -> bool:
        """Check if quiz is finished."""
        return self.current_question >= len(self.questions)
    
    def get_results(self) -> Dict:
        """Get final quiz results."""
        return {
            'total_questions': len(self.questions),
            'correct_answers': self.correct_answers,
            'score_percent': self.get_score(),
            'passed': self.get_score() >= 70,  # 70% pass score
        }

class LearningCurriculum:
    """Complete curriculum for learning Braille."""
    
    LESSONS = {
        1: BrailleLesson(
            1, "Alphabet Basics",
            "Learn the basic 26 letters of the English alphabet",
            {
                'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
                'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
                'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
                'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
                'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
                'z': '⠵'
            },
            DifficultyLevel.BEGINNER
        ),
        2: BrailleLesson(
            2, "Numbers",
            "Learn how numbers are represented in Braille",
            {
                '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
                '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚'
            },
            DifficultyLevel.BEGINNER
        ),
        3: BrailleLesson(
            3, "Punctuation",
            "Master punctuation marks in Braille",
            {'.': '⠲', ',': '⠂', '!': '⠖', '?': '⠦'},
            DifficultyLevel.INTERMEDIATE
        ),
    }
    
    def __init__(self):
        """Initialize curriculum with lessons."""
        self.lessons = list(self.LESSONS.values())
    
    @staticmethod
    def get_lesson(lesson_id: int) -> BrailleLesson:
        return LearningCurriculum.LESSONS.get(lesson_id)
    
    @staticmethod
    def get_all_lessons() -> List[BrailleLesson]:
        return list(LearningCurriculum.LESSONS.values())
    
    @staticmethod
    def get_lessons_by_difficulty(difficulty: DifficultyLevel) -> List[BrailleLesson]:
        return [l for l in LearningCurriculum.LESSONS.values() 
                if l.difficulty == difficulty]

class LearningTracker:
    """Track user's learning progress."""
    
    def __init__(self):
        self.completed_lessons = set()
        self.quiz_scores = {}
        self.flashcard_stats = {}
    
    def mark_lesson_complete(self, lesson_id: int):
        """Mark a lesson as completed."""
        self.completed_lessons.add(lesson_id)
    
    def record_quiz_score(self, lesson_id: int, score: float):
        """Record quiz score for a lesson."""
        self.quiz_scores[lesson_id] = score
    
    def get_progress(self) -> Dict:
        """Get overall learning progress."""
        total_lessons = len(LearningCurriculum.LESSONS)
        completed = len(self.completed_lessons)
        
        avg_quiz_score = 0
        if self.quiz_scores:
            avg_quiz_score = sum(self.quiz_scores.values()) / len(self.quiz_scores)
        
        return {
            'lessons_completed': completed,
            'total_lessons': total_lessons,
            'completion_percent': (completed / total_lessons) * 100,
            'avg_quiz_score': avg_quiz_score,
        }
    
    def get_recommendations(self) -> List[str]:
        """Get learning recommendations based on progress."""
        progress = self.get_progress()
        recommendations = []
        
        if progress['completion_percent'] == 0:
            recommendations.append("Start with Lesson 1: Alphabet Basics")
        elif progress['avg_quiz_score'] < 50:
            recommendations.append("Review previous lessons - your scores are below 50%")
        elif progress['completion_percent'] < 50:
            recommendations.append(f"You're {progress['completion_percent']:.0f}% done - keep going!")
        else:
            recommendations.append("Great progress! Try advanced lessons.")
        
        return recommendations

# Global tracker instance
learning_tracker = LearningTracker()
