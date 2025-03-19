# 📊 Accounting Manager (المحاسب الشامل)

Accounting Manager is a powerful and easy-to-use web application for managing accounts and inventory.  
It provides detailed financial reports, stock tracking, and user-friendly dashboards.  

## 🚀 Features
- **Financial Reports:** Sales, purchases, profit & loss analysis.
- **Inventory Management:** Track stock levels and movements.
- **Company Customization:** Add logos, customize invoices and reports.
- **Multi-user Support:** Role-based access control.
- **Modern Dashboard:** Interactive charts for financial insights.
- **API Integration:** REST API support for seamless integration.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/loma-gerhold/Elshamel.git
cd Elshamel
```
2️⃣ Create & Activate Virtual Environment

- **On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```
- **On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```
4️⃣ Apply Migrations & Run Server

```bash
python manage.py migrate
python manage.py runserver
```
Now, open your browser and visit: http://127.0.0.1:8000/ 🎉

🌍 Deploying on PythonAnywhere

1️⃣ Push Your Project to GitHub
If you haven't pushed your project yet, run the following:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/your-repository.git
git push -u origin main
```
2️⃣ Configure PythonAnywhere
1.Log in to PythonAnywhere and go to the Web section.
2.Create a new web app → Choose Manual Configuration → Select Python 3.x.
3.Upload your code via Git:
```bash
git clone https://github.com/your-username/your-repository.git
```
4.Set up the virtual environment:
```bash
cd your-repository
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
5.Edit the WSGI configuration in PythonAnywhere to point to your Django/Flask app
6.Restart the web app to apply changes.

📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

✨ Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.
For major changes, please open an issue first to discuss what you'd like to improve.

📩 Contact

For any inquiries or support, contact me at:

📧 lamindzru@gmail.com

🌍 [MY Website](https://files.dz-gsmdz.site/)








