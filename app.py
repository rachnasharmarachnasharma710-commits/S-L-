
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from urllib.parse import quote
from database import init_db, list_products, create_order, add_feedback, get_feedback
from admin import render_admin

ROOT = Path(__file__).parent
st.set_page_config(page_title="SŌLÉ — Botanical Bath & Body", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")
init_db()

def local_image(filename):
    path = ROOT / "images" / (filename or "")
    if path.exists():
        return "images/" + filename
    return "images/rose.svg"

def price_after(p):
    return round(float(p["price"]) * (1-int(p["discount"] or 0)/100), 2)

def money(value):
    return f"₹{value:,.2f}"

def add_cart(p):
    cart = st.session_state.setdefault("cart", {})
    key = str(p["id"])
    cart[key] = cart.get(key, 0) + 1
    st.toast(f'{p["name"]} added to your bag')

def inject_css():
    css = (ROOT/"assets"/"style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_css()

# Top navigation
nav1, nav2, nav3 = st.columns([2.2,5,2.2])
with nav1:
    st.markdown('<div class="brand-mark">✳ <span>SŌLÉ</span><small>BOTANICAL BATH & BODY</small></div>', unsafe_allow_html=True)
with nav2:
    page = st.radio("Navigation", ["Home","Shop","About","Contact","Feedback","Admin"], horizontal=True, label_visibility="collapsed")
with nav3:
    st.markdown(f'<div class="bag-label">✧ YOUR BAG · {sum(st.session_state.get("cart",{}).values())} ITEMS</div>', unsafe_allow_html=True)

st.markdown('<div class="topline"></div>', unsafe_allow_html=True)

def product_card(p, idx):
    image = local_image(p.get("image"))
    discount = int(p.get("discount",0))
    final = price_after(p)
    cols = st.columns([1,1])
    with cols[0]:
        st.image(image, use_container_width=True)
    with cols[1]:
        if discount:
            st.markdown(f'<span class="sale-tag">{discount}% OFF</span>', unsafe_allow_html=True)
        st.markdown(f'### {p["name"]}')
        st.caption(p["category"])
        st.write(p["description"])
        if discount:
            st.markdown(f'<div class="price">{money(final)} <del>{money(p["price"])}</del></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="price">{money(final)}</div>', unsafe_allow_html=True)
        x,y = st.columns(2)
        with x:
            if st.button("Add to bag", key=f'add_{p["id"]}_{idx}', use_container_width=True):
                add_cart(p)
        with y:
            if st.button("Buy now", key=f'buy_{p["id"]}_{idx}', use_container_width=True, type="primary"):
                add_cart(p)
                st.session_state.page_checkout = True
                st.rerun()

def render_cart():
    cart = st.session_state.setdefault("cart", {})
    products = {str(p["id"]):p for p in list_products(include_inactive=True)}
    st.markdown("## Your shopping bag")
    if not cart:
        st.info("Your bag is waiting for something lovely.")
        return
    total = 0
    for key in list(cart.keys()):
        p = products.get(key)
        if not p:
            cart.pop(key, None)
            continue
        q1,q2,q3,q4 = st.columns([4,1,1,1])
        with q1:
            st.write(f'**{p["name"]}**')
            st.caption(money(price_after(p)) + " each")
        with q2:
            if st.button("−", key=f"minus_{key}"):
                cart[key] -= 1
                if cart[key] <= 0: cart.pop(key)
                st.rerun()
        with q3:
            st.write(f'**{cart.get(key,0)}**')
        with q4:
            if st.button("+", key=f"plus_{key}"):
                cart[key] += 1
                st.rerun()
        if key in cart:
            line = price_after(p)*cart[key]
            total += line
            st.caption(f"Line total: {money(line)}")
    st.markdown(f'<div class="total-box">ORDER TOTAL <strong>{money(total)}</strong></div>', unsafe_allow_html=True)
    st.session_state.cart_total = total
    st.markdown("### Delivery details")
    with st.form("checkout_form"):
        name = st.text_input("Customer name")
        mobile = st.text_input("Mobile number", max_chars=10, placeholder="10-digit mobile number")
        address = st.text_area("Full delivery address")
        submit = st.form_submit_button("Place order", type="primary", use_container_width=True)
        if submit:
            if not name.strip() or not address.strip() or not (mobile.isdigit() and len(mobile)==10):
                st.error("Please enter your name, full address and a valid 10-digit mobile number.")
            elif not cart:
                st.error("Your bag is empty.")
            else:
                items=[]
                for key,qty in cart.items():
                    p=products.get(key)
                    if p:
                        items.append({"name":p["name"],"qty":qty,"unit_price":price_after(p),
                                      "line_total":round(price_after(p)*qty,2)})
                order_id=create_order(name.strip(),mobile,address.strip(),items,round(total,2))
                st.session_state.cart={}
                st.session_state.last_order=order_id
                st.success(f"Thank you! Your order #{order_id} has been received.")
                st.rerun()

def render_home():
    st.markdown("""
    <section class="hero">
      <div class="hero-copy">
        <span class="eyebrow">THE ART OF EVERYDAY RITUALS</span>
        <h1>Make room for<br><em>beautifully</em> simple.</h1>
        <p>Thoughtfully crafted bathing essentials, inspired by nature and made for your everyday pause.</p>
        <div class="hero-note">BOTANICAL · MINDFUL · FEEL-GOOD</div>
      </div>
      <div class="hero-art"><div class="sun"></div><div class="soap-shape"></div><div class="leaf leaf-one">✦</div><div class="leaf leaf-two">✧</div></div>
    </section>
    """, unsafe_allow_html=True)
    if st.button("EXPLORE THE COLLECTION  →", type="primary"):
        st.session_state.shop_jump=True
        st.rerun()
    st.markdown('<div class="section-head"><div><span class="eyebrow">CURATED FOR YOU</span><h2>Best-loved essentials</h2></div><span>01 / THE COLLECTION</span></div>', unsafe_allow_html=True)
    products=list_products()
    featured=sorted(products,key=lambda p:p["discount"],reverse=True)[:4]
    grid=st.columns(2)
    for i,p in enumerate(featured):
        with grid[i%2]:
            product_card(p,i)
    st.markdown('<section class="quote-band"><span>✳</span><h2>Small rituals.<br><em>Beautiful</em> feelings.</h2><p>Bring a little more care into the everyday.</p></section>', unsafe_allow_html=True)
    st.markdown("### Fresh arrivals")
    for i,p in enumerate(products[:2]):
        with st.container(border=True):
            product_card(p,100+i)
    st.markdown("### A little love from our customers")
    reviews=get_feedback()
    if reviews:
        for r in reviews[:3]:
            st.markdown(f'<div class="review">“{r["message"]}”<br><small>— {r["customer_name"] or "Happy customer"} · {"★"*r["rating"]}</small></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="review">“A lovely addition to my everyday routine.”<br><small>— A happy customer · ★★★★★</small></div>',unsafe_allow_html=True)

def render_shop():
    st.markdown('<span class="eyebrow">SHOP THE COLLECTION</span><h1 class="page-title">Find your daily ritual.</h1>',unsafe_allow_html=True)
    search=st.text_input("Search products",placeholder="Try rose, neem, handmade…")
    categories=["All","Herbal","Floral","Premium","Handmade","Daily Care"]
    category=st.selectbox("Shop by category",categories)
    products=list_products(search,category)
    st.caption(f"{len(products)} products")
    if not products: st.info("No products found. Try another search.")
    cols=st.columns(2)
    for i,p in enumerate(products):
        with cols[i%2]:
            with st.container(border=True):
                product_card(p,i+200)

def render_about():
    st.markdown('<span class="eyebrow">OUR PHILOSOPHY</span><h1 class="page-title">Care, made<br><em>considerate.</em></h1>',unsafe_allow_html=True)
    st.markdown("""We believe a bath can be more than a routine. SŌLÉ is a little reminder to slow down, breathe deeply and make everyday care feel special.

Our collection brings together botanical inspiration, comforting fragrances and thoughtful design. We keep the experience simple: discover a bar you love, make it part of your ritual, and enjoy the pause.""")
    st.markdown('<div class="quote-band"><h2>Good things begin<br>with a <em>little care.</em></h2></div>',unsafe_allow_html=True)

def render_contact():
    st.markdown('<span class="eyebrow">WE’RE HERE TO HELP</span><h1 class="page-title">Say hello.</h1>',unsafe_allow_html=True)
    st.write("Questions about an order, a product or a gift? We’d love to hear from you.")
    phone=st.text_input("Store WhatsApp number (with country code)",placeholder="e.g. 919876543210")
    msg=st.text_area("Your message",placeholder="How can we help?")
    if phone and msg:
        wa=f"https://wa.me/{''.join(c for c in phone if c.isdigit())}?text={quote(msg)}"
        st.link_button("Chat with us on WhatsApp",wa,use_container_width=True)
    st.info("Add your real WhatsApp number here or configure it in the app before publishing.")

def render_feedback():
    st.markdown('<span class="eyebrow">KIND WORDS</span><h1 class="page-title">Share your experience.</h1>',unsafe_allow_html=True)
    with st.form("feedback_form"):
        name=st.text_input("Your name")
        rating=st.slider("Your rating",1,5,5)
        message=st.text_area("Your feedback")
        if st.form_submit_button("Send feedback",type="primary"):
            if message.strip():
                add_feedback(name.strip(),rating,message.strip())
                st.success("Thank you for sharing your feedback.")
                st.rerun()
            else: st.error("Please write a short message.")

if page=="Home":
    render_home()
elif page=="Shop":
    render_shop()
elif page=="About":
    render_about()
elif page=="Contact":
    render_contact()
elif page=="Feedback":
    render_feedback()
elif page=="Admin":
    render_admin()

# Cart always available below content
st.markdown('<div class="footer-rule"></div>',unsafe_allow_html=True)
with st.expander(f"🛍️ Shopping bag · {sum(st.session_state.get('cart',{}).values())} items", expanded=bool(st.session_state.get("page_checkout",False))):
    render_cart()
st.markdown("""
<footer class="site-footer">
 <div><div class="footer-brand">✳ SŌLÉ</div><p>BOTANICAL BATH & BODY</p></div>
 <div><b>THE GOOD STUFF</b><p>Thoughtful bathing essentials<br>for everyday rituals.</p></div>
 <div><b>EXPLORE</b><p>Shop · Our story · Get in touch</p></div>
 <div><b>FOLLOW YOUR RITUAL</b><p>Made with care. Shared with love.</p></div>
 <small>© 2026 SŌLÉ. Storefront starter brand — personalise before launch.</small>
</footer>
""",unsafe_allow_html=True)
