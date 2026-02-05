import streamlit as st
import requests
from datetime import datetime, timezone

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

API_URL = "http://127.0.0.1:8000"

MENU = {
    "Burger": 199,
    "Pizza": 299,
    "Pasta": 249,
    "Biryani": 279
}

st.set_page_config(
    page_title="Food Delivery Support AI",
    layout="centered"
)

st.title("Food Delivery Support AI")
st.caption("Customer Support System")

if "user_id" not in st.session_state:
    st.session_state.user_id = "user_123"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "order" not in st.session_state:
    st.session_state.order = None

if "force_menu" not in st.session_state:
    st.session_state.force_menu = False


def get_latest_order():
    try:
        res = requests.get(
            f"{API_URL}/latest-order/{st.session_state.user_id}",
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            if data:
                return data
    except:
        pass
    return None


def cancel_order(order_id):
    try:
        res = requests.post(
            f"{API_URL}/cancel-order/{order_id}",
            timeout=5
        )
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None


def parse_created_at(order):
    created = order.get("created_at") if order else None
    if not created:
        return None
    try:
        dt = datetime.fromisoformat(created)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def format_eta_countdown(order):
    if not order:
        return ""

    status = order.get("status")
    if status == "CANCELLED":
        return "N/A"
    if status == "DELIVERED":
        return "Delivered"

    created = parse_created_at(order)
    if not created:
        return order.get("eta", "")

    now = datetime.now(timezone.utc)
    elapsed = (now - created).total_seconds()

    total_delivery_seconds = 600
    remaining = max(0, int(total_delivery_seconds - elapsed))
    if remaining == 0:
        return "Delivered"

    minutes = remaining // 60
    seconds = remaining % 60
    return f"{minutes:02d}:{seconds:02d}"


def ensure_autorefresh(interval_ms=1000):
    if st_autorefresh is not None:
        st_autorefresh(interval=interval_ms, key="eta_refresh")
        return

    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=interval_ms, key="eta_refresh")
        return


if st.session_state.order is None and not st.session_state.force_menu:
    st.session_state.order = get_latest_order()

if st.session_state.order and st.session_state.order.get("status") not in ["CANCELLED", "DELIVERED"]:
    latest = get_latest_order()
    if latest:
        st.session_state.order = latest


if st.session_state.order:

    col1, col2 = st.columns([4, 1])

    with col1:
        order = st.session_state.order
        eta_display = format_eta_countdown(order)
        st.info(
            f"Order #{order['order_id']} | {order['item']} | Status: {order['status']} | ETA: {eta_display}"
        )

    with col2:
        if st.button("Back to Menu"):
            if order.get("status") not in ["CANCELLED", "DELIVERED"]:
                cancel_order(order["order_id"])

            st.session_state.order = None
            st.session_state.messages = []
            st.session_state.force_menu = True
            st.rerun()

    if order.get("status") not in ["CANCELLED", "DELIVERED"]:
        ensure_autorefresh(interval_ms=1000)




else:

    st.subheader("Menu")

    item = st.selectbox(
        "Select an item",
        list(MENU.keys())
    )

    price = MENU[item]

    st.write(f"Price: ₹{price}")

    if st.button("Place Order", use_container_width=True):

        payload = {
            "user_id": st.session_state.user_id,
            "item": item,
            "price": price
        }

        try:
            res = requests.post(
                f"{API_URL}/create-order",
                json=payload,
                timeout=5
            )

            if res.status_code == 200:
                st.session_state.order = res.json()
                st.session_state.messages = []
                st.session_state.force_menu = False
                st.rerun()
            else:
                st.error(res.text)

        except requests.exceptions.RequestException:
            st.error("Backend is not reachable")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


if st.session_state.order:

    user_input = st.chat_input("Describe your issue")

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "user_id": st.session_state.user_id,
                    "message": user_input
                },
                timeout=10
            )

            if response.status_code == 200:
                bot_reply = response.json()["reply"]
            else:
                bot_reply = "Support service is currently unavailable."

        except requests.exceptions.RequestException:
            bot_reply = "Unable to connect to support."

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply
        })

        latest = get_latest_order()
        if latest:
            st.session_state.order = latest

        with st.chat_message("assistant"):
            st.write(bot_reply)

else:
    st.warning("Place an order to enable customer support.")
