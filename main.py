import streamlit as st
from PIL import Image
from datetime import datetime
from logic.scanner import scan_receipt
from logic.chef import suggest_recipes
from database.operations import add_items_to_pantry, get_current_inventory, update_item_count

st.set_page_config(page_title="Smart Pantry Chef", page_icon="👨‍🍳", layout="wide")

# --- 1. SMART NOTIFICATION BANNER ---
# This runs immediately when the user opens the app
current_hour = datetime.now().hour
if 5 <= current_hour < 11:
    greeting = "🌅 Good Morning! Time for Breakfast."
elif 11 <= current_hour < 16:
    greeting = "☀️ Good Afternoon! Thinking about Lunch?"
else:
    greeting = "🌙 Good Evening! Let's make Dinner."

st.title("🤖 Smart Pantry Agent")
st.info(f"🔔 **{greeting}** check your kitchen tab to see what we can cook!")

menu = st.sidebar.radio("Navigate", ["📸 Scan Receipt", "🍳 My Kitchen"])

# ==========================================
# PAGE 1: SCANNER (Unchanged)
# ==========================================
if menu == "📸 Scan Receipt":
    st.header("Upload Receipt")
    uploaded_file = st.file_uploader("Take a photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=350)
        with open("temp_receipt.jpg", "wb") as f: f.write(uploaded_file.getbuffer())
        if st.button("🚀 Analyze Receipt"):
            with st.spinner("Reading receipt..."):
                try:
                    data = scan_receipt("temp_receipt.jpg")
                    if data:
                        add_items_to_pantry(data)
                        st.success(f"✅ Merged {len(data)} items!")
                except Exception as e: st.error(f"Error: {e}")

# ==========================================
# PAGE 2: KITCHEN (Major Upgrade)
# ==========================================
elif menu == "🍳 My Kitchen":
    
    # Inventory Section
    st.subheader("📦 Inventory")
    inventory = get_current_inventory()
    if not inventory:
        st.warning("Pantry is empty.")
    else:
        for item in inventory:
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1: st.markdown(f"**{item['item_name']}**")
            with c2: st.markdown(f"x{item['quantity']}")
            with c3: 
                if st.button("➖", key=f"d{item['id']}"): 
                    update_item_count(item['id'], -1)
                    st.rerun()
            with c4: 
                if st.button("➕", key=f"i{item['id']}"): 
                    update_item_count(item['id'], 1)
                    st.rerun()

    st.divider()

    # Chef Section
    st.subheader("👨‍🍳 Chef's Recommendations")
    
    c1, c2 = st.columns(2)
    with c1: pace = st.selectbox("Time available?", ["Fast (20m)", "Medium (40m)", "Slow (1h+)"])
    with c2: craving = st.text_input("Craving?", placeholder="e.g. Spicy, Indian, Italian...")

    if st.button("✨ Generate Detailed Recipes"):
        with st.spinner("👨‍🍳 Consulting Michelin Chef..."):
            prefs = {"pace": pace, "people": 2, "occasion": craving if craving else "Dinner"}
            suggestions = suggest_recipes(prefs)
            
            if "recipes" in suggestions:
                for recipe in suggestions["recipes"]:
                    # Create a card for the recipe
                    with st.expander(f"🍽️ {recipe['name']} ({recipe['time_minutes']} min)", expanded=False):
                        st.write(f"*{recipe['description']}*")
                        
                        # Ingredients
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("✅ **Use:** " + ", ".join(recipe['used_ingredients']))
                        with col_b:
                            st.markdown("🛒 **Need:** " + ", ".join(recipe['missing_ingredients']))
                        
                        st.divider()
                        
                        # --- STEP BY STEP GUIDE ---
                        st.markdown("### 📝 Instructions")
                        for idx, step in enumerate(recipe.get('steps', [])):
                            # We use checkboxes so user can tick them off as they cook
                            step_text = f"**Step {idx+1}:** {step['step']} "
                            meta_text = f"*(🔥 {step['heat']} | ⏰ {step['time']})*"
                            st.checkbox(f"{step_text} {meta_text}", key=f"{recipe['name']}_{idx}")
                        
                        st.divider()
                        
                        # --- SPECIFIC YOUTUBE LINK ---
                        # Uses the specific query from the AI
                        query = recipe.get('youtube_query', recipe['name'] + ' recipe')
                        yt_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                        st.markdown(f"### 📺 [Watch Tutorial: {query}]({yt_url})")
            else:
                st.error("Chef error. Try again.")