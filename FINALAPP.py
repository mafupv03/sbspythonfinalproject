import streamlit as st
import openai
from datetime import datetime, timedelta
import os
from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Swap App", layout="wide")

# ---------------------- API Key ----------------------
with st.sidebar:
    st.session_state["api_key"] = st.text_input("Place your OpenAI API key here", type="password")

if st.session_state["api_key"]:
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=st.session_state["api_key"]
    )
else:
    st.error("No API key provided!!")

# ---------------------- Session State ----------------------
if "products" not in st.session_state:
    st.session_state.products = [
        {"name": "Leather Backpack", "category": "Accessories", "description": "A stylish brown leather backpack.", "location": "Barcelona", "image": "images/leatherbackpackimg.png", "rating": 4.5, "available": datetime(2025, 6, 15)},
        {"name": "Blue Denim Jacket", "category": "Clothing", "description": "Trendy denim jacket.", "location": "Barcelona", "image": "images/bluedenimjacket.png", "rating": 4.2, "available": datetime(2025, 6, 18)},
        {"name": "Red Running Shoes", "category": "Footwear", "description": "Comfy and light.", "location": "Madrid", "image": "images/redrunningshoes.png", "rating": 4.7, "available": datetime(2025, 6, 20)},
        {"name": "Black Denim Shorts", "category": "Clothing", "description": "Black denim shorts, casual and cool.", "location": "Barcelona", "image": "images/blackshorts.png", "rating": 4.3, "available": datetime(2025, 6, 21)},
        {"name": "Red Shirt", "category": "Clothing", "description": "Bright red shirt, perfect for summer.", "location": "Barcelona", "image": "images/redshirt.png", "rating": 4.4, "available": datetime(2025, 6, 22)},
        {"name": "Beige Beach Hat", "category": "Accessories", "description": "Lightweight beige beach hat.", "location": "Barcelona", "image": "images/beachhat.png", "rating": 4.6, "available": datetime(2025, 6, 22)},
        {"name": "Black Leather Jacket", "category": "Clothing", "description": "Classic black leather jacket.", "location": "Barcelona", "image": "images/blackleatherjacket.png", "rating": 4.8, "available": datetime(2025, 6, 23)},
        {"name": "Plaid Skirt", "category": "Clothing", "description": "Trendy plaid skirt for casual outings.", "location": "Barcelona", "image": "images/plaidskirt.png", "rating": 4.5, "available": datetime(2025, 6, 24)}
    ]

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Touraj Vaziri",
        "email": "touraj@sbs.barcelona",
        "status": "Active",
        "credits": 30,
        "history": [1, 2],
        "my_items": [],
        "reserved": []
    }

if "reviews" not in st.session_state:
    st.session_state.reviews = []

if "lockers" not in st.session_state:
    st.session_state.lockers = [
        {"name": "Locker A", "address": "123 Main St", "city": "Barcelona"},
        {"name": "Locker B", "address": "456 Side St", "city": "Madrid"},
    ]

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# ---------------------- Tabs ----------------------
tabs = st.tabs([
    "Discover",
    "User Profile",
    "Add New Item",
    "Reserved Items",
    "Community",
    "Payment"
])

# ------------------ TAB 1: DISCOVER ------------------
with tabs[0]:
    st.markdown("<h1 style='text-align: center;'>SWITCH'D</h1>", unsafe_allow_html=True)
    search_query = st.text_input("SEARCH", label_visibility="collapsed", placeholder="Search items near you...")
    st.markdown("## Items near you!")
    filtered_products = [p for p in st.session_state.products if search_query.lower() in p["name"].lower()] if search_query else st.session_state.products
    cols = st.columns(4)
    for idx, product in enumerate(filtered_products):
        with cols[idx % 4]:
            st.image(product["image"], caption=product["name"], use_container_width=True)
            st.write(f"{product['name']}")
            if st.button(f"Suggest Similar (AI)", key=f"sim_{idx}"):
                prompt = f"Suggest secondhand items similar to: {product['description']}"
                try:
                    response = model.invoke(input=prompt)
                    st.markdown("**Similar Items:**")
                    st.info(response.content)
                except Exception as e:
                    st.error("AI suggestion failed. " + str(e))
            if st.button(f"Click to Reserve {product['name']}", key=f"reserve_{idx}"):
                if product not in st.session_state.user_profile['reserved']:
                    st.session_state.user_profile['reserved'].append(product)
                    pickup_start = product["available"].strftime("%B %d")
                    pickup_end = (product["available"] + timedelta(days=3)).strftime("%B %d")
                    locker = st.session_state.lockers[0]
                    st.success(f"✅ Reserved *{product['name']}!*\n\n📦 Pick up between **{pickup_start}–{pickup_end}** at *{locker['name']}*, {locker['address']}, {locker['city']}.")
                else:
                    st.info("You have already reserved this item.")

# ------------------ TAB 2: USER PROFILE ------------------
with tabs[1]:
    st.markdown("<h2>USER PROFILE</h2>", unsafe_allow_html=True)
    profile_cols = st.columns([1, 2, 1])
    with profile_cols[0]:
        st.image("images/TourajProfilePic.png", caption="Profile Image")
    with profile_cols[1]:
        st.write(f"**{st.session_state.user_profile['name']}**")
        st.write(st.session_state.user_profile['email'])
        st.write(st.session_state.user_profile['status'])
    with profile_cols[2]:
        st.metric(label="SWITCHD CREDITS", value=f"€{st.session_state.user_profile['credits']}")
        st.metric(label="ITEMS EXCHANGED", value=str(len(st.session_state.user_profile['history'])))

    st.markdown("### MY ITEMS")
    item_cols = st.columns(4)
    # Show static items
    with item_cols[0]:
        st.image("images/blueshirt.png", caption="Blue Shirt")
    with item_cols[1]:
        st.image("images/yellowrunningshoes.png", caption="Yellow Running Shoes")
    with item_cols[2]:
        st.image("images/bikingshorts.png", caption="Biking Shorts")
    with item_cols[3]:
        if st.button("➕", help="Add new item"):
            st.session_state.adding_item = True

    # Show user's added items
    if st.session_state.user_profile["my_items"]:
        st.markdown("#### Your Added Items")
        added_cols = st.columns(4)
        for i, item in enumerate(st.session_state.user_profile["my_items"]):
            with added_cols[i % 4]:
                st.image(item["image"], caption=item["name"])

# Show input fields if user is adding an item
if st.session_state.get("adding_item", False):
    st.markdown("### Add New Item")
    new_name = st.text_input("Item Name", key="new_item_name")
    new_desc = st.text_area("Item Description", key="new_item_desc")
    new_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="new_item_image")
    if st.button("Submit Item"):
        if new_name and new_desc and new_image:
            img_path = f"temp_{new_image.name}"
            with open(img_path, "wb") as f:
                f.write(new_image.read())
            st.session_state.user_profile['my_items'].append({
                "name": new_name,
                "description": new_desc,
                "image": img_path
            })
            st.session_state.adding_item = False
            st.rerun()
        else:
            st.warning("Please fill in all fields and upload an image.")

# ------------------ TAB 3: ADD NEW ITEM ------------------
with tabs[2]:
    st.markdown("<h2>ADD A NEW ITEM</h2>", unsafe_allow_html=True)
    with st.form("new_item_form"):
        name = st.text_input("Item name")
        category = st.selectbox("Category", ["Clothing", "Accessories", "Footwear"])
        description = st.text_area("Description")
        location = st.text_input("Location")
        available_date = st.date_input("Available from")
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Add Item")
        if submitted and name and image_file:
            img_path = f"temp_{image_file.name}"
            with open(img_path, "wb") as f:
                f.write(image_file.read())
            new_product = {
                "name": name,
                "category": category,
                "description": description,
                "location": location,
                "image": img_path,
                "rating": 0,
                "available": datetime.combine(available_date, datetime.min.time())
            }
            st.session_state.user_profile["my_items"].append(new_product)
            st.success("Item added!")

# ------------------ TAB 4: RESERVED ITEMS ------------------
with tabs[3]:
    st.markdown("<h2>YOUR RESERVED ITEMS</h2>", unsafe_allow_html=True)
    if st.session_state.user_profile['reserved']:
        for item in st.session_state.user_profile['reserved']:
            st.image(item["image"], caption=item["name"])
            st.markdown(f"- *{item['name']}* ({item['category']}) – {item['location']}, Available from {item['available'].strftime('%B %d')}")
    else:
        st.info("No items reserved yet.")

# ------------------ TAB 5: COMMUNITY ------------------
with tabs[4]:
    st.markdown("<h2>CONNECT WITH OTHER SWITCHRS!</h2>", unsafe_allow_html=True)
    usernames = ["Marianna Tsareva", "Yuliana Evdokimova", "Esma Smailbegovic", "Kayla Jaco", "Romana Zdarska"]
    switches = [3, 15, 4, 10, 4]
    ratings = [3, 5, 2, 4, 5]
    for i in range(len(usernames)):
        row = st.columns([1, 3, 3])
        with row[0]:
            st.image("images/profileicon.png", caption="Icon")
        with row[1]:
            st.markdown(f"**{usernames[i]}**")
            st.write(f"{switches[i]} SWITCHES")
        with row[2]:
            st.write("⭐" * ratings[i])

# ------------------ TAB 6: PAYMENT ------------------
with tabs[6]:
    st.markdown("<h2>CHECK OUT</h2>", unsafe_allow_html=True)
    cart_items = ["ITEM NAME", "ITEM NAME", "ITEM NAME"]
    prices = [5, 5, 5]
    total = sum(prices)
    for i in range(len(cart_items)):
        row = st.columns([1, 5, 1])
        with row[0]:
            st.image("images/itemicon.png", caption="Image")
        with row[1]:
            st.write(cart_items[i])
        with row[2]:
            st.write(f"€{prices[i]}")
    st.markdown(f"### TOTAL: €{total}")

    payment_method = st.radio("Choose Payment Method", ["Card", "PayPal", "Switch'd Credits"])
    if payment_method == "Card":
        with st.form("card_form"):
            st.subheader("Enter Card Information")
            card_number = st.text_input("Card Number")
            expiry = st.text_input("Expiry Date (MM/YY)")
            cvv = st.text_input("CVV", type="password")
            name = st.text_input("Name on Card")
            pay = st.form_submit_button("Pay Now")
            if pay:
                if card_number and expiry and cvv and name:
                    st.success("Payment successful via Card! ✅")
                else:
                    st.error("Please fill out all card fields.")
    elif payment_method == "PayPal":
        with st.form("paypal_form"):
            st.subheader("Enter PayPal Information")
            email = st.text_input("PayPal Email")
            password = st.text_input("PayPal Password", type="password")
            pay = st.form_submit_button("Pay Now")
            if pay:
                if email and password:
                    st.success("Payment successful via PayPal! ✅")
                else:
                    st.error("Please enter your PayPal credentials.")
    elif payment_method == "Switch'd Credits":
        if st.button("Pay with Switch'd Credits"):
            if st.session_state.user_profile['credits'] >= total:
                st.session_state.user_profile['credits'] -= total
                st.success("Paid using Switch’d credits!")
            else:
                st.error("Not enough credits.")



