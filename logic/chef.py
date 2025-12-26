import sys
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.operations import get_current_inventory

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def suggest_recipes(username, user_preferences, people_count):
    inventory = get_current_inventory(username)
    if not inventory:
        return {"error": "Pantry is empty."}
    
    ingredients_list = ", ".join([f"{i['item_name']}" for i in inventory])
    
    # Time Logic
    current_hour = datetime.now().hour
    if 5 <= current_hour < 11: time_meal = "Breakfast"
    elif 11 <= current_hour < 16: time_meal = "Lunch"
    else: time_meal = "Dinner"
    meal_type = user_preferences.get('occasion', time_meal)

    prompt = f"""
    You are a Chef.
    Cooking for: {people_count} People.
    My Ingredients: {ingredients_list}.
    Staples: [Salt, Pepper, Oil, Sugar].
    
    Context: {time_meal}, Type: {meal_type}.
    
    Task: Suggest 5 recipes SCALED for {people_count} people.
    
    Return JSON:
    {{
        "recipes": [
            {{
                "name": "Recipe Name",
                "time_minutes": 20,
                "description": "Description",
                "used_ingredients": ["Rice", "Spinach"],
                "steps": ["Step 1...", "Step 2..."]
            }}
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return []