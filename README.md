
# SŌLÉ — Premium Soap Store

A responsive Streamlit storefront with a Python backend and SQLite database.

## Included
- Home, shop, about, contact and customer feedback sections
- Product search and category filtering
- Product cards with discounts, add-to-bag and buy-now actions
- Quantity controls, cart total and checkout form
- Orders stored in SQLite
- Password-protected admin area for products, sales summary and order statuses
- Local SVG product artwork, CSS theme and mobile styling

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Open the local address shown in the terminal.

## Admin password
Set an environment variable before running:
- macOS/Linux: `export ADMIN_PASSWORD='your-long-password'`
- Windows PowerShell: `$env:ADMIN_PASSWORD='your-long-password'`

On Streamlit Community Cloud, open **App → Settings → Secrets** and add:
```toml
ADMIN_PASSWORD = "your-long-unique-password"
```
Never publish your real password in GitHub or this ZIP.

## Deploy to Streamlit Community Cloud
1. Create a GitHub account and a new **public or private** repository.
2. Upload the contents of this ZIP to the repository root (not the ZIP file itself).
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**, choose your repository, branch and `app.py`.
5. Deploy. In the app settings, add `ADMIN_PASSWORD` under **Secrets**.
6. Reboot the app after saving secrets.

## Important SQLite hosting note
The app uses SQLite as requested. Streamlit Community Cloud's local filesystem is not guaranteed to be durable across app rebuilds, restarts or redeployments. For a real live shop, take regular database backups and consider moving orders/products to a managed persistent database (for example PostgreSQL) before relying on it for business-critical records. Do not assume the SQLite file is a permanent cloud backup.

## Before going live
- Replace the sample brand name SŌLÉ, logo and sample descriptions with your real shop identity.
- Set your real WhatsApp number in the Contact section.
- Review product prices, stock and descriptions in Admin.
- Configure a strong admin password in Streamlit Secrets.
- Test an order end-to-end before sharing the website.
- Add your privacy, shipping, cancellation and return policies.

## Project structure
```text
soapique_store/
├── app.py
├── admin.py
├── database.py
├── requirements.txt
├── README.md
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── assets/
│   └── style.css
└── images/
    ├── rose.svg
    ├── aloe.svg
    ├── neem.svg
    ├── charcoal.svg
    ├── herbal.svg
    ├── sandalwood.svg
    ├── handmade.svg
    └── classic.svg
```
