import spacy
from .models import InterviewQ
from pymongo import MongoClient
import random

class InterviewAI:
    def __init__(self):
        self.question_count = 0
        self.genralqueasked=0
        self.responses = {}
        self.mustqueasked =0
        self.asked_questions = set()  # Track asked questions
        self.asked_questions_order=""
        self.asked_topics = set()  # Track asked topics to ensure diversity
      
        self.nlp = spacy.load("en_core_web_sm")  # Load the spaCy language model

        self.keywords = {
                  "general": [
                  "Why did you apply for this job?",
                  "What makes you the best candidate for this job? or Why should we hire you?",
                  "What are some of your strengths?",
                  "What are some of your Weaknesses?",
                  "In your opinion, what is the ideal company? or What makes you want to work for this company?",
                  "What do you know about our company?",
                  "Do you prefer an entrepreneurial or structured company culture?",
                  "Describe your perfect work environment.",
                  "What are your hobbies and how do you think they relate to this job?",
                  "Can you tell me about a project you worked on in your free time that you're particularly proud of?",
                  "What are some things you're passionate about outside of work or school?",
                  "Have you ever volunteered for a cause you're passionate about? Can you tell me about your experience?",
                  "How do you stay current with industry developments and trends in your free time?"
                  ],
                  "must_ask_que":[


                  "What do you like to do in your free time?",
                  "Can you describe a project you worked on that demonstrates your problem-solving skills?"
                  ],
                  "volunteer":[

                  "Can you describe a time when you worked with a team to achieve a goal in a volunteer or community setting?",
                  "How do you think your volunteer experience has prepared you for this role?"
                  ],

                  "flexibility": [
                  "How do you handle ambiguity or uncertainty in a project or task?",
                  "Have you ever had to pivot or adjust your approach mid-project due to new information or feedback? How did you handle it?"
                  ],
                  "communication": [
                  "Can you give an example of a time when you had to communicate complex information to a non-technical audience? How did you approach it?",
                  "How do you ensure that your message is understood and received correctly by your team or stakeholders?"
                  ],
                  "communicate": [
                  "Can you give an example of a time when you had to communicate complex information to a non-technical audience? How did you approach it?",
                  "How do you ensure that your message is understood and received correctly by your team or stakeholders?"
                  ],
                  "teamwork": [
                  "Describe a project where you had to work with a cross-functional team to achieve a common goal. What was your role, and how did you contribute to the team's success?",
                  "How do you handle conflicts or disagreements within a team? Can you give an example of a time when you had to navigate a difficult team dynamic?"
                  ],
                  "problem": [
                  "Can you walk me through your thought process when approaching a complex problem? How do you identify the root cause and develop a solution?",
                  "Describe a situation where you had to think outside the box to come up with a creative solution. What was the outcome, and what did you learn from the experience?"
                  ],
                  "adaptability": [
                  "Can you give an example of a time when you had to adapt to a new process or system? How did you handle the change, and what did you learn from the experience?",
                  "How do you stay flexible and open to new ideas or approaches when working on a project or task?"
                  ],
                  "adaptabile": [
                  "Can you give an example of a time when you had to adapt to a new process or system? How did you handle the change, and what did you learn from the experience?",
                  "How do you stay flexible and open to new ideas or approaches when working on a project or task?"
                  ],
                  "leader": [
                  "Describe a time when you had to lead a team or project. What was your approach to leadership, and how did you motivate your team to achieve the desired outcome?",
                  "How do you delegate tasks and responsibilities to team members? Can you give an example of a time when you had to make a tough decision as a leader?"
                  ],
                  "leadership": [
                  "Describe a time when you had to lead a team or project. What was your approach to leadership, and how did you motivate your team to achieve the desired outcome?",
                  "How do you delegate tasks and responsibilities to team members? Can you give an example of a time when you had to make a tough decision as a leader?"
                  ],
                  "time": [
                  "Can you walk me through your process for prioritizing tasks and managing your time? How do you stay organized and focused?",
                  "Describe a situation where you had to juggle multiple projects or deadlines. How did you manage your time, and what was the outcome?",
                  "Can you give an example of a time when you struggled to manage your time effectively? What were the consequences, and what did you learn from the experience?",
                  "How do you prioritize tasks and allocate your time, and what tools or systems do you use to stay organized?"
                  ],
                  "timetable": [
                  "Can you walk me through your process for prioritizing tasks and managing your time? How do you stay organized and focused?",
                  "Describe a situation where you had to juggle multiple projects or deadlines. How did you manage your time, and what was the outcome?",
                  "Can you give an example of a time when you struggled to manage your time effectively? What were the consequences, and what did you learn from the experience?",
                  "How do you prioritize tasks and allocate your time, and what tools or systems do you use to stay organized?"
                  ],
                  "detail": [
                  "Can you give an example of a time when your attention to detail caught a mistake or error that others might have missed? What was the impact of your attention to detail?",
                  "How do you ensure that you're thorough and accurate in your work? Can you describe your quality control process?"
                  ],
                  "focus": [
                  "Can you give an example of a time when your attention to detail caught a mistake or error that others might have missed? What was the impact of your attention to detail?",
                  "How do you ensure that you're thorough and accurate in your work? Can you describe your quality control process?"
                  ],
                  "creativity": [
                  "Can you describe a time when you came up with a innovative solution to a problem? What was the outcome, and what did you learn from the experience?",
                  "How do you foster creativity and idea generation within a team or organization?"
                  ],
                  "creative": [
                  "Can you describe a time when you came up with a innovative solution to a problem? What was the outcome, and what did you learn from the experience?",
                  "How do you foster creativity and idea generation within a team or organization?"
                  ],
                  "resilience": [
                  "Can you give an example of a time when you faced a setback or failure? How did you bounce back, and what did you learn from the experience?",
                  "How do you handle stress and pressure in the workplace? Can you describe a situation where you had to manage your emotions and stay focused?"
                  ],
                  "accountability": [
                  "Can you describe a time when you took ownership of a mistake or error? How did you rectify the situation, and what did you learn from the experience?",
                  "How do you hold yourself and others accountable for meeting deadlines and achieving goals? Can you give an example of a time when you had to address a performance issue with a team member?"
                  ],
                  "accountabile": [
                  "Can you describe a time when you took ownership of a mistake or error? How did you rectify the situation, and what did you learn from the experience?",
                  "How do you hold yourself and others accountable for meeting deadlines and achieving goals? Can you give an example of a time when you had to address a performance issue with a team member?"
                  ],

                  "procrastination": [
                  "Can you describe a situation where you put off a task or project until the last minute? What were the consequences, and what did you learn from the experience?",
                  "How do you plan to overcome procrastination in the future? What strategies or tools do you use to stay on track and meet deadlines?"
                  ],
                  "impulsiveness": [
                  "Can you give an example of a time when you acted impulsively and regretted it? What did you learn from the experience, and how do you approach decision-making differently now?",
                  "How do you balance the need to take action quickly with the need to think carefully and consider the consequences of your actions?"
                  ],
                  "impulsive": [
                  "Can you give an example of a time when you acted impulsively and regretted it? What did you learn from the experience, and how do you approach decision-making differently now?",
                  "How do you balance the need to take action quickly with the need to think carefully and consider the consequences of your actions?"
                  ],
                  "perfectionism": [
                  "Can you describe a situation where your perfectionism held you back from completing a task or project? What did you learn from the experience, and how do you prioritize tasks now?",
                  "How do you balance the need for quality with the need to meet deadlines and deliver results?"
                  ],
                  "perfect": [
                  "Can you describe a situation where your perfectionism held you back from completing a task or project? What did you learn from the experience, and how do you prioritize tasks now?",
                  "How do you balance the need for quality with the need to meet deadlines and deliver results?"
                  ],
                  "delegation": [
                  "Can you give an example of a time when you struggled to delegate tasks to others? What was the outcome, and what did you learn from the experience?",
                  "How do you identify tasks that can be delegated, and what strategies do you use to empower others to take ownership of those tasks?"
                  ],
                  "public": [
                  "Can you describe a situation where you felt nervous or uncomfortable speaking in front of a group? What did you do to prepare, and how did you handle your nerves?",
                  "How do you plan to improve your public speaking skills, and what resources or training have you sought out to help you overcome this weakness?"
                  ],
                  "motivate": [
                  "Can you describe a situation where you struggled to stay motivated or engaged? What did you do to overcome the slump, and what did you learn from the experience?",
                  "How do you stay motivated and focused on your goals, and what strategies do you use to overcome obstacles or setbacks?"
                  ],
                  "feedback": [
                  "Can you give an example of a time when you received constructive feedback that was difficult to hear? How did you respond, and what did you learn from the experience?",
                  "How do you seek out feedback from others, and what do you do with the feedback you receive?"
                  ],
                  "emotional": [
                  "Can you describe a situation where you struggled to understand or manage your emotions? What were the consequences, and what did you learn from the experience?",
                  "How do you recognize and respond to the emotions of others, and what strategies do you use to build strong relationships?"
                  ],
                  "failure": [
                  "Can you give an example of a time when you failed at a task or project? What did you learn from the experience, and how did you apply those lessons to future endeavors?",
                  "How do you approach failure, and what strategies do you use to learn from your mistakes and improve your performance over time?"
                  ],
                  "internship": [
                  "Can you tell me about your internship experience with that company? What were your responsibilities, and what did you achieve during your time there?",
                  "How did you apply your skills and knowledge during the internship, and what did you learn from the experience?",
                  "What were some of the most significant challenges you faced during the internship, and how did you overcome them?",
                  "Can you describe a specific project or task you worked on during the internship? What was your role, and what were the outcomes?",
                  "How did the internship experience prepare you for a full-time role, and what skills or knowledge did you gain that you can apply to this position?"
                  ],
                  "project":[
                  "What were some of the biggest challenges you faced during the project, and how did you overcome them?",
                  "What was your role in the project, and how did you contribute to its success?",
                  "Can you describe the team's dynamics and how you coordinated with your team members to achieve the project's objectives?",
                  "What technology or tools did you use during the project, and how did you leverage them to achieve the desired outcomes?",
                  "When did the project start, and what were the key milestones and deadlines?",
                  "What was the project's objective, and how did it align with the company's overall goals?",
                  "What were some of the advantages and benefits of the project, and how did it impact the company or its customers?",
                  "What is the future scope of the project, and how do you see it evolving in the next few years?",
                  "What resources did you use during the project, and how did you manage them to achieve the desired outcomes?",
                  "When did the project start?",
                  "When did the project end?",
                  "What were the outcomes of the project, and how did they meet the project's objectives?"
                  ],

                  "Company_Fit": [
                  "In your opinion, what is the ideal company? or What makes you want to work for this company?",
                  "What do you know about our company?",
                  "Do you prefer an entrepreneurial or structured company culture?",
                  "Describe your perfect work environment."
                  ],

                  "job_Experience": [
                  "Can you tell me about your previous work experience with that company? What were your responsibilities, and what did you achieve during your time there?",
                  "How did you contribute to the company's goals and objectives, and what impact did you make?",
                  "What did you learn from your experience with that company, and how has it prepared you for this role?",
                  "Can you describe a specific project or initiative you worked on with that company? What was your role, and what were the outcomes?",
                  "How did you handle specific challenge during your time with that company? What did you learn from the experience?"
                  ],

                  "behavioral": [
                  "Tell me about the most difficult decision you have had to make recently. How did you reach a decision?",
                  "Have you ever been given an assignment that was too difficult for you? What was your solution and why?",
                  "Tell me about an instance when you had to deal with conflict in the workplace.",
                  "Give me an example of a time when you made a mistake at work. How did you handle it?",
                  "How would you handle a situation where you were required to complete multiple tasks by the end of the day, but it would be impossible to finish all of them?",
                  "If you discovered that your company was doing something illegal, like fraud, what would you do?",
                  "If, while at a business lunch, you ordered a rare steak but you received one that was well done, how would you react?",
                  "Tell me about the most difficult time in your life. How did you get through it?",
                  "What would you do if your supervisor asked you to do something that you didn't agree with?",
                  "What is your strategy for working with people who annoy you?",
                  "Tell me about a time that you failed. What did you learn from it?",
                  "How do you approach giving someone difficult feedback?",
                  "Have you ever been a part of a team where there is a member not doing their part? How did you react?",
                  "Describe a time when your work or performance was criticized.",
                  "Tell me about a time when you went above and beyond what was expected of you at work.",
                  "Tell me about the last project that you led. What was the final result?",
                  "Give me an example of a time that you showed leadership.",
                  "How do you manage stress? What do you like to do in your free time?",
                  "Who are your personal heroes and why?",
                  "What is the first thing you would do if you were to win the lottery?",
                  "If you could travel anywhere in the world right now, where would you go?",
                  "Describe the difference between exceptional and good.",
                  "Outside of your career, what has been your greatest accomplishment?",
                  "Who has had the biggest impact on your career?",
                  "If you could only choose five words to describe your character, what would they be?",
                  "What is your life's mission statement?",
                  "Tell me about your lifelong aspirations.",
                  "Describe what you are most proud of.",
                  "What personality types do you work well with and why?",
                  "What tools and strategies do you use to stay organized?",
                  "Do you prefer an entrepreneurial or structured company culture?",
                  "Describe your perfect work environment.",
                  "What is your work style?"
                  ],



                  "music": [
                  "What kind of music do you like listening to?",
                  "Do you play any musical instruments?",
                  "Who's your favorite band or artist?",
                  "Have you been to any concerts or music festivals recently?"
                  ]
                  ,

                  "sport": [
                  "What's your favorite sport to watch or play?",
                  "Do you have a favorite team or player?",
                  "Have you participated in any sports tournaments or competitions?"
                  ]
                  ,

                  "outdoor": [
                  "Do you enjoy hiking, camping, or other outdoor activities?",
                  "Have you gone on any recent trips or adventures?",
                  "What do you like about spending time outdoors?"
                  ]
                  ,

                  "game": [
                  "What kind of games do you like to play?",
                  "Do you have a favorite gaming platform or console?",
                  "Have you participated in any gaming tournaments or events?"
                  ]
                  ,

                  "gameing": [
                    "What kind of games do you like to play?",
                    "Do you have a favorite gaming platform or console?",
                    "Have you participated in any gaming tournaments or events?"
                  ]
                  ,

                  "read": [
                  "What kind of books do you like to read?",
                  "Do you have a favorite author or series?",
                  "How often do you read for pleasure?"
                  ]
                  ,

                  "travel": [
                  "Have you traveled to any new places recently?",
                  "Where would you like to travel to next?",
                  "What do you like about exploring new destinations?"
                  ]



                  }
 
 
    def generate_followup(self, exkeywords):
        questions = []
        followups = None

        for key in exkeywords:
            if key in self.keywords:
                followups = random.choice(self.keywords[key])
                if isinstance(followups, dict):
                    for sub_key, sub_followups in followups.items():
                        for followup in sub_followups:
                            if followup not in self.asked_questions and self.is_diverse_topic(followup):
                                priority = self.calculate_priority(key, followup)
                                questions.append((priority, followup))
                else:
                    if followups not in self.asked_questions and self.is_diverse_topic(followups):
                        priority = self.calculate_priority(key, followups)
                        questions.append((priority, followups))

        questions.sort(reverse=True, key=lambda x: x[0])
        final_questions = questions[0][1] if questions else None

        if not final_questions:
            que = random.choice(self.keywords.get("general", []))
            if que not in self.asked_questions and self.is_diverse_topic(que):
                final_questions = que

        self.genralqueasked += 1
        return final_questions

    def genrate_behave_quetion(self):
        final_questions = None
        que = random.choice(self.keywords.get("behavioral", []))
        if que not in self.asked_questions and self.is_diverse_topic(que):
            final_questions = que
        return final_questions

    def genrate_Company_Experience_quetion(self):
        final_questions = None
        que = random.choice(self.keywords.get("job_Experience", []))
        if que not in self.asked_questions and self.is_diverse_topic(que):
            final_questions = que
        return final_questions

    def genrate_must_ask_que_quetion(self):

        final_questions = None
        for que in self.keywords.get("must_ask_que", []):
            if que not in self.asked_questions and self.is_diverse_topic(que):
                final_questions = que
        self.mustqueasked += 1
        return final_questions

    def genrate_Company_Fit_quetion(self):
        que = random.choice(self.keywords.get("Company_Fit", []))
        if que not in self.asked_questions:
            return que

    def is_diverse_topic(self, question):
        topic = self.extract_topic(question)
        if topic not in self.asked_topics:
            self.asked_topics.add(topic)
            return True
        return False

    def calculate_priority(self, keyword, question):
        keyword_doc = self.nlp(keyword)
        question_doc = self.nlp(question)
        similarity = keyword_doc.similarity(question_doc)
        return similarity

    def extract_topic(self, question):
        doc = self.nlp(question)
        topics = [token.lemma_.lower() for token in doc if token.pos_ in {"NOUN", "PROPN"}]
        return topics[0] if topics else ""

    def ask_next_question(self, response_text):
        if self.question_count >= 15:
            return self.endinterviewlast()
   
        keywords = self.extract_keywords(response_text)
        if self.question_count == 0:
            question = "Tell me about yourself."
        elif self.genralqueasked == 4 and not hasattr(self, 'experience_question_asked'):
            question = "Do you have any work-related experience, any internship, or company job? Please elaborate it."
            self.experience_question_asked = True  # Mark that this question has been asked
        elif self.question_count == 3 and self.mustqueasked < 2:

            question = self.genrate_must_ask_que_quetion()

        elif self.genralqueasked < 4:
            if not keywords:
                question = self.genrate_behave_quetion()
            question = self.generate_followup(keywords)
            
        else:
            question = self.genrate_behave_quetion()

        if question is None:
            question = self.genrate_Company_Fit_quetion()

        # If still no question, retry generating another question
        if question is None:
            return self.ask_next_question(response_text)

        # If a valid question is generated, add it to asked questions and increment the count
        self.responses[self.asked_questions_order] = response_text
        
        self.asked_questions_order=question
        self.asked_questions.add(question)
        self.question_count += 1
        
        return question

    def endinterviewlast(self):
        
        # Reset state for a new interview
        self.question_count = 0
        self.genralqueasked = 0
        self.mustqueasked = 0
        self.asked_questions.clear()
        self.asked_topics.clear()
        return "Thank you for participating in the interview."
    
     # Save the dictionary to the Django model

    def extract_keywords(self, response):
        doc = self.nlp(response)
        keywords = set()

        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            if token.pos_ in {"NOUN", "PROPN", "VERB"}:  # Extract nouns, proper nouns, and verbs
                keywords.add(token.lemma_.lower())

        return list(keywords)