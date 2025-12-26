import streamlit as st
from datetime import datetime
from itertools import groupby
from logic.scanner import scan_receipt, save_receipt_image
from logic.chef import suggest_recipes
from database.operations import (
    register_user, login_user, init_pantry_db,
    add_items_to_pantry, get_current_inventory, 
    update_item_count, deduct_ingredients, get_grocery_list
)

st.set_page_config(page_title="Smart Pantry OS", page_icon="🍳", layout="wide")

if 'user' not in st.session_state:
    st.session_state['user'] = None

# --- AUTH (Unchanged) ---
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔐 Smart Kitchen Access</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Unlock Kitchen"):
                if login_user(username, password):
                    st.session_state['user'] = username
                    init_pantry_db(username)
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    with tab2:
        with st.form("reg_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            if st.form_submit_button("Create Account"):
                if register_user(new_user, new_pass):
                    st.success("Account created!")
                else:
                    st.error("Username taken.")

if st.session_state['user'] is None:
    login_page()
else:
    user = st.session_state['user']
    st.sidebar.title(f"👤 Chef {user}")
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.rerun()
    menu = st.sidebar.radio("Navigation", ["📸 Scan Receipt", "📦 Inventory", "👨‍🍳 Chef Mode", "🛒 Restock List"])

    # 1. SCANNER
    if menu == "📸 Scan Receipt":
        st.header("📥 Upload Receipt")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])
        if uploaded_file:
            path = save_receipt_image(uploaded_file, user)
            st.image(path, width=300)
            if st.button("Process Receipt"):
                with st.spinner("Analyzing..."):
                    items = scan_receipt(path)
                    if items:
                        add_items_to_pantry(user, items)
                        st.success(f"Added {len(items)} items!")
                    else:
                        st.error("Failed to read receipt.")

    # 2. INVENTORY (With Decimal Support)
    elif menu == "📦 Inventory":
        st.header(f"📦 {user}'s Pantry")
        inventory = get_current_inventory(user)
        if not inventory:
            st.info("Pantry is empty.")
        else:
            inventory.sort(key=lambda x: x['category'])
            for category, items in groupby(inventory, key=lambda x: x['category']):
                st.subheader(category)
                for item in items:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 1, 2])
                        c1.markdown(f"**{item['item_name']}**")
                        c2.text(f"{round(item['quantity'], 2)} {item['unit']}")
                        
                        with c3:
                            if category in ['Produce', 'Pantry', 'Dairy']:
                                cols = st.columns(3)
                                if cols[0].button("¼", key=f"q_{item['id']}"):
                                    update_item_count(user, item['id'], -0.25)
                                    st.rerun()
                                if cols[1].button("½", key=f"h_{item['id']}"):
                                    update_item_count(user, item['id'], -0.5)
                                    st.rerun()
                                if cols[2].button("All", key=f"f_{item['id']}"):
                                    update_item_count(user, item['id'], -100.0)
                                    st.rerun()
                            else:
                                if st.button("Use 1", key=f"use_{item['id']}"):
                                    update_item_count(user, item['id'], -1.0)
                                    st.rerun()

    # 3. CHEF MODE (TIME LOGIC RESTORED! 🕒)
    elif menu == "👨‍🍳 Chef Mode":
        st.header("👨‍🍳 Master Chef")
        
        # --- SMART TIME LOGIC ---
        now = datetime.now()
        current_hour = now.hour
        formatted_time = now.strftime("%I:%M %p") # e.g., "11:30 AM"

        # Determine greeting and default selection
        if 5 <= current_hour < 11: 
            greeting = "Good Morning! ☀️"
            default_index = 0 # Breakfast
        elif 11 <= current_hour < 16: 
            greeting = "Good Afternoon! 🥗"
            default_index = 1 # Lunch
        elif 16 <= current_hour < 22: 
            greeting = "Good Evening! 🍝"
            default_index = 2 # Dinner
        else:
            greeting = "Late Night? 🌙"
            default_index = 3 # Snack

        st.info(f"🕒 It is **{formatted_time}**. {greeting}")

        # Controls
        c1, c2, c3 = st.columns(3)
        
        # Auto-select the meal based on time, but let user change it
        meal_pref = c1.selectbox(
            "Meal Type", 
            ["Breakfast", "Lunch", "Dinner", "Snack"], 
            index=default_index
        )
        
        time_pref = c2.select_slider("Time Available", options=["15m", "30m", "1h", "Slow Cook"])
        people = c3.number_input("People", min_value=1, max_value=10, value=2)

        if st.button("Suggest Recipes"):
            with st.spinner(f"Chef is finding {meal_pref} ideas..."):
                prefs = {"occasion": meal_pref, "pace": time_pref}
                st.session_state['recipes'] = suggest_recipes(user, prefs, people)
        
        if 'recipes' in st.session_state:
            for r in st.session_state['recipes']['recipes']:
                with st.expander(f"🍽️ {r['name']} ({r['time_minutes']} min)"):
                    st.write(f"*{r['description']}*")
                    st.markdown("### Instructions")
                    for step in r['steps']:
                        st.write(f"- {step}")
                    
                    if st.button(f"I Cooked This (For {people})", key=f"cook_{r['name']}"):
                        logs = deduct_ingredients(user, r['used_ingredients'], people)
                        st.success("Inventory Updated!")
                        for log in logs:
                            st.caption(log)

    # 4. RESTOCK
    elif menu == "🛒 Restock List":
        st.header("🛒 Shopping List")
        grocery_items = get_grocery_list(user)
        if not grocery_items:
            st.success("All stocked up!")
        else:
            for item in grocery_items:
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"❌ **{item['item_name']}** ({item['category']})")
                if c2.button("Restock Full", key=f"buy_{item['id']}"):
                    update_item_count(user, item['id'], 1.0)
                    st.rerun()