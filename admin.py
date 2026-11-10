
import os
import streamlit as st
import pandas as pd
from database import list_products, save_product, delete_product, get_orders, update_order_status

def admin_login():
    st.markdown("### 🔐 Admin access")
    st.caption("Sign in to manage your store.")
    password = st.text_input("Admin password", type="password", key="admin_password")
    expected = st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD", ""))
    if not expected:
        st.warning("Set ADMIN_PASSWORD in Streamlit Secrets before using the admin panel.")
        return False
    if st.button("Sign in", type="primary", use_container_width=True):
        if password == expected:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return st.session_state.get("admin_authenticated", False)

def render_admin():
    if not st.session_state.get("admin_authenticated", False):
        if not admin_login():
            return
    st.markdown("## Store control room")
    if st.button("Sign out"):
        st.session_state.admin_authenticated = False
        st.rerun()

    products = list_products(include_inactive=True)
    orders = get_orders()
    sales = sum(o["total"] for o in orders if o["status"] != "Cancelled")
    a,b,c = st.columns(3)
    a.metric("Total orders", len(orders))
    b.metric("Total products", len(products))
    c.metric("Sales value", f"₹{sales:,.0f}")

    tab1, tab2 = st.tabs(["Products", "Orders"])
    with tab1:
        st.markdown("### Add / edit product")
        choices = {"➕ New product": None}
        choices.update({f'{p["id"]} · {p["name"]}': p for p in products})
        selected = st.selectbox("Choose product", list(choices.keys()))
        current = choices[selected] or {}
        with st.form("product_form"):
            name = st.text_input("Product name", current.get("name",""))
            category = st.selectbox("Category", ["Herbal","Floral","Premium","Handmade","Daily Care"],
                                    index=(["Herbal","Floral","Premium","Handmade","Daily Care"].index(current.get("category","Herbal")) if current.get("category","Herbal") in ["Herbal","Floral","Premium","Handmade","Daily Care"] else 0))
            price = st.number_input("Price (₹)", min_value=1.0, value=float(current.get("price",149)))
            discount = st.number_input("Discount (%)", min_value=0, max_value=90, value=int(current.get("discount",0)))
            description = st.text_area("Description", current.get("description",""))
            image = st.text_input("Image filename in images/ (e.g. rose.svg)", current.get("image","rose.svg"))
            stock = st.number_input("Stock", min_value=0, value=int(current.get("stock",50)))
            active = st.checkbox("Visible in shop", value=bool(current.get("active",1)))
            submitted = st.form_submit_button("Save product", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Product name is required.")
                else:
                    save_product(dict(name=name.strip(),category=category,price=price,discount=discount,
                                      description=description,image=image,stock=stock,active=int(active)),
                                 current.get("id"))
                    st.success("Product saved.")
                    st.rerun()
        if current and st.button("Delete selected product", type="secondary"):
            delete_product(current["id"])
            st.success("Product deleted.")
            st.rerun()

    with tab2:
        st.markdown("### Customer orders")
        if not orders:
            st.info("No orders yet.")
        for order in orders:
            with st.expander(f'Order #{order["id"]} · {order["customer_name"]} · ₹{order["total"]:,.2f}'):
                st.write(f'**Mobile:** {order["mobile"]}')
                st.write(f'**Address:** {order["address"]}')
                st.write(f'**Placed:** {order["created_at"]}')
                st.write("**Items:**")
                for item in order["items"]:
                    st.write(f'• {item["name"]} × {item["qty"]} — ₹{item["line_total"]:,.2f}')
                statuses = ["Received","Confirmed","Packed","Shipped","Delivered","Cancelled"]
                idx = statuses.index(order["status"]) if order["status"] in statuses else 0
                new_status = st.selectbox("Order status", statuses, index=idx, key=f'status_{order["id"]}')
                if st.button("Update status", key=f'update_{order["id"]}'):
                    update_order_status(order["id"], new_status)
                    st.success("Order status updated.")
                    st.rerun()
