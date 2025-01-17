from ai71 import AI71  
import os
import json
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv('.env')

# API KEY
AI71_API_KEY = os.getenv('AI71_API_KEY')
client = AI71(AI71_API_KEY)

def llm_response(prompt,temp):
    response = client.chat.completions.create(
        model="tiiuae/falcon-180B-chat", 
        messages=[
            {"role": "system", "content": "You are a teaching assistant."},
            {"role": "user", "content": prompt},
                ],
        temperature=temp)
    return response.choices[0].message.content

def calculate_marks_per_topic(filtered_df):
    # Group by 'topic' and sum the marks
    marks_per_topic = filtered_df.groupby('topic')['mark'].sum().reset_index()
    
    # Calculate the number of questions per topic
    num_questions_per_topic = filtered_df.groupby('topic').size().reset_index(name='num_questions')
    
    # Merge the number of questions with the marks per topic
    marks_per_topic = marks_per_topic.merge(num_questions_per_topic, on='topic')
    
    # Calculate the total possible marks for each topic
    marks_per_topic['total_possible_marks'] = marks_per_topic['num_questions'] * 10
    
    return marks_per_topic

def llm_to_get_feedback(summary):
    # Construct the prompt for the LLM
    prompt = (
        f"Based on the following suggestions summary, provide a JSON response with"
        f"improvements and strengths:\n\nSummary: {summary}\n\n"
        "Provide the response as a JSON object with keys strengths and gaps. Both the keys should contain points based on the provided summary to improve."
    )
    
    temp=0.9
    
    # Extract the response
    feed_back = llm_response(prompt,temp)
    
    # Step 1: Clean the string by removing unwanted characters
    cleaned_text = feed_back.replace('\n', '').replace('} {', '},{').replace('}{', '},{')
        
    # Step 2: Convert cleaned text to a JSON list
    feed_back_json = json.loads(f"[{cleaned_text}]")
    
    return feed_back_json

def evaluate_answer_using_model(question, given_answer, actual_answer):
    prompt = (
        f"Evaluate the following answer for the question '{question}':\n\n"
        f"Answer: {given_answer}\n\n"
        f"Correct Answer: {actual_answer}\n\n"
        "Provide a JSON response with the following fields:\n"
        "- mark: A value out of 10 for overall answer accuracy.\n"
        "- conceptual_understanding: A value out of 10 assessing understanding of the concept.\n"
        "- problem_solving: A value out of 10 evaluating the problem-solving approach.\n"
        "- clarity_of_expression: A value out of 10 judging the clarity of expression.\n"
        "- suggestions: Improvements needed for the answer.\n"
        "- Be strict in evaluation when you provide the marks."
    )
    
    # Extract the response
    evaluation_response = llm_response(prompt,temp=0.5)
    
    return evaluation_response
