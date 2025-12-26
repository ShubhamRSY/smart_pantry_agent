import base64
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def save_receipt_image(uploaded_file, username):
    """Saves to receipts/username/filename.jpg"""
    # Create user specific folder
    folder = os.path.join("receipts", username.lower().strip())
    os.makedirs(folder, exist_ok=True)
    
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def scan_receipt(image_path):
    # (Same prompt as before, no changes needed to logic, just the folder above)
    print(f"📸 Scanning receipt: {image_path}")
    base64_image = encode_image(image_path)

    prompt = """
    Analyze this grocery receipt.
    1. Extract items.
    2. CATEGORIZE STRICTLY:
       - 'Dairy': Milk, Cheese, Butter.
       - 'Produce': Fruits, Vegetables, Spinach.
       - 'Snacks': Chips, Nuts. (NEVER Fridge).
       - 'Meat': Chicken, Beef.
       - 'Pantry': Rice, Pasta, Oil, Spices, Bread.
       - 'Frozen': Ice Cream.
       - 'Household': Paper towels.
    
    Return JSON list:
    [{"clean_name": "Basmati Rice", "category": "Pantry", "quantity": 1, "unit": "bag"}]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}},
                    ],
                }
            ],
            max_tokens=1500,
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get('items', data)
    except Exception as e:
        print(f"❌ Error: {e}")
        return []