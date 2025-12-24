import sys
import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.operations import get_current_inventory

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# We use the smart model for better logic
model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')

def suggest_recipes(user_preferences):
    inventory = get_current_inventory()
    
    if not inventory:
        return {"error": "Pantry is empty."}
    
    ingredients_list = ", ".join([f"{item['item_name']} (x{item['quantity']})" for item in inventory])
    print(f"   🥦 Cooking with: {ingredients_list}")

    # Time Logic
    current_hour = datetime.now().hour
    if 5 <= current_hour < 11: time_context = "Breakfast"
    elif 11 <= current_hour < 16: time_context = "Lunch"
    else: time_context = "Dinner"

    # --- THE NEW SUPER PROMPT ---
    prompt = f"""
    You are a Michelin-star Home Chef. 
    I have these ingredients: {ingredients_list}.
    
    CONTEXT:
    - Meal: {time_context}
    - Pace: {user_preferences.get('pace', 'Fast')}
    - Craving: {user_preferences.get('occasion', 'Any')}
    
    TASK:
    Suggest 3 HIGH-QUALITY, REAL recipes. Do not invent weird combinations.
    If I have Paneer, suggest real Indian dishes. If I have Pasta, suggest real Italian dishes.
    
    REQUIREMENTS:
    1. 'youtube_query': Create a specific search term to find the best video. 
       - BAD: "Paneer recipe"
       - GOOD: "Authentic Paneer Butter Masala restaurant style recipe"
    2. 'steps': Provide step-by-step instructions.
       - Include HEAT LEVEL (Low/Med/High).
       - Include EXACT TIMING (e.g., "5 mins").
    
    Return STRICT JSON:
    {{
        "recipes": [
            {{
                "name": "Recipe Name",
                "time_minutes": 30,
                "difficulty": "Medium",
                "description": "Appetizing description.",
                "used_ingredients": ["List..."],
                "missing_ingredients": ["List..."],
                "youtube_query": "Best authentic [Dish Name] video recipe",
                "steps": [
                    {{"step": "Heat pan and add oil", "heat": "High", "time": "2 mins"}},
                    {{"step": "Add onions and saute until golden", "heat": "Medium", "time": "5 mins"}}
                ]
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"❌ Error: {e}")
        return []