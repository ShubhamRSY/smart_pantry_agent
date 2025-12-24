import os
import json
import google.generativeai as genai
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# We use the stable model as discussed

model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
def search_product_online(query):
    """
    The 'Search' box in your diagram.
    Uses DuckDuckGo (Free) to find out what a mysterious product is.
    """
    print(f"   🔍 Searching web for: '{query}'...")
    try:
        results = DDGS().text(query, max_results=1)
        if results:
            return results[0]['body'] # Return the snippet describing the item
    except Exception as e:
        print(f"   ⚠️ Search failed: {e}")
    return "Unknown Product"

def scan_receipt(image_path):
    """
    The Main Pipeline: Image -> Vision -> Search -> JSON
    """
    print(f"\n📸 Processing Receipt: {image_path}")
    
    # --- STEP 1: UPLOAD IMAGE TO GEMINI ---
    print("   🚀 Uploading to Gemini Vision...")
    myfile = genai.upload_file(image_path)
    
    # --- STEP 2: EXTRACTION PROMPT ---
    # We ask for a specific JSON format to make Database storage easy.
    prompt = """
    Analyze this grocery receipt. Extract all food and grocery items.
    Return a STRICT JSON list of objects. Do not use Markdown formatting.
    
    For each item, extract:
    1. 'raw_name': The text exactly as written on the receipt.
    2. 'clean_name': A normalized, generic name (e.g., convert 'KIRK S MILK' to 'Milk').
    3. 'category': Choose from [Dairy, Produce, Meat, Pantry, Frozen, Beverage, Household, Other].
    4. 'quantity': The amount (e.g., '1 gal', '2 count', '12 oz'). If not clear, put '1'.
    5. 'confidence': 'high' if you are sure what it is, 'low' if the name is cryptic (like a code or abbreviation).
    
    Example format:
    [
        {"raw_name": "Avocado Lg", "clean_name": "Avocado", "category": "Produce", "quantity": "1", "confidence": "high"},
        {"raw_name": "X99-231", "clean_name": "Unknown", "category": "Other", "quantity": "1", "confidence": "low"}
    ]
    """
    
    result = model.generate_content([myfile, prompt])
    
    # --- STEP 3: PARSE THE JSON ---
    try:
        # Clean up if Gemini adds ```json ``` blocks
        json_text = result.text.replace("```json", "").replace("```", "").strip()
        items = json.loads(json_text)
    except Exception as e:
        print(f"❌ Error parsing JSON from AI: {e}")
        return []

    # --- STEP 4: THE NORMALIZATION LOOP (Your Diagram's 'Search' Logic) ---
    final_inventory = []
    
    for item in items:
        # If the AI was confused (Low Confidence), we trigger the Search Agent
        if item['confidence'] == 'low' or item['clean_name'] == 'Unknown':
            print(f"   ⚠️ Low confidence detected for: {item['raw_name']}")
            
            # Perform the search
            search_context = search_product_online(f"grocery item {item['raw_name']}")
            
            # Ask Gemini to fix the name using the search result
            fix_prompt = f"I have a grocery item labeled '{item['raw_name']}'. I searched online and found this description: '{search_context}'. Based on this, what is the 'clean_name' and 'category'? Return JSON: {{'clean_name': '...', 'category': '...'}}"
            
            fix_result = model.generate_content(fix_prompt)
            try:
                fixed_data = json.loads(fix_result.text.replace("```json", "").replace("```", "").strip())
                item['clean_name'] = fixed_data.get('clean_name', item['raw_name'])
                item['category'] = fixed_data.get('category', 'Other')
                print(f"   ✅ Fixed: {item['raw_name']} -> {item['clean_name']}")
            except:
                print("   ❌ Could not fix item name.")
        
        final_inventory.append(item)

    return final_inventory

# --- TESTER BLOCK ---
if __name__ == "__main__":
    # Update this with the path you just gave me
    test_image_path = "/Users/disastershubz/Downloads/smart_pantry_agent/test_receipt.jpg"
    
    # Check if file exists to be safe
    if os.path.exists(test_image_path):
        print(f"✅ Found file at: {test_image_path}")
        data = scan_receipt(test_image_path)
        print("\n--- FINAL JSON OUTPUT ---")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: File not found at {test_image_path}")