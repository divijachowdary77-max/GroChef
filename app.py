from flask import Flask, render_template, request, redirect, session
import os
import cv2
import pytesseract
import re

app = Flask(__name__)

# ====================================
# SECRET KEY
# ====================================

app.secret_key = "grochef_secret"

# ====================================
# UPLOAD FOLDER
# ====================================

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ====================================
# TESSERACT PATH
# ====================================

pytesseract.pytesseract.tesseract_cmd = (
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

# ====================================
# CREATE FOLDERS
# ====================================

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ====================================
# USERS FILE
# ====================================

if not os.path.exists("users.txt"):
    open("users.txt", "w").close()

# ====================================
# RECIPES DATABASE
# ====================================

quick_recipes = [

# BREAKFAST

{
    "name": "Bread Omelette",
    "ingredients": ["bread", "egg"],
    "category": "Breakfast",
    "time": "10 mins",
    "image": "https://tse2.mm.bing.net/th/id/OIP.41xhluaCQ82NybHi5dcFuAHaHa?r=0&w=600&h=600&rs=1&pid=ImgDetMain&o=7&rm=3"
},

{
    "name": "French Toast",
    "ingredients": ["bread", "milk"],
    "category": "Breakfast",
    "time": "10 mins",
    "image": "https://sugarspunrun.com/wp-content/uploads/2023/08/French-Toast-recipe-4-of-5.jpg"
},

{
    "name": "Egg Sandwich",
    "ingredients": ["bread", "egg"],
    "category": "Breakfast",
    "time": "15 mins",
    "image": "https://tse3.mm.bing.net/th/id/OIP.Itb3RN14-VJXIyQmfIeFaQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
},

{
    "name": "Poha",
    "ingredients": ["poha"],
    "category": "Breakfast",
    "time": "15 mins",
    "image": "https://tse2.mm.bing.net/th/id/OIP.D4d96NYaNFNCqbSRzl3jZAHaLH?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
},

{
    "name": "Masala Oats",
    "ingredients": ["oats"],
    "category": "Breakfast",
    "time": "10 mins",
    "image": "https://smithakalluraya.com/wp-content/uploads/2023/03/masala-oats-recipe-1080x1735.jpg"
},

# LUNCH

{
    "name": "Egg Rice",
    "ingredients": ["rice", "egg"],
    "category": "Lunch",
    "time": "15 mins",
    "image": "https://www.cookerru.com/wp-content/uploads/2022/07/egg-fried-rice-main-preview.jpg"
},

{
    "name": "Dal Rice",
    "ingredients": ["rice", "kandipappu"],
    "category": "Lunch",
    "time": "20 mins",
    "image": "https://myheartbeets.com/wp-content/uploads/2020/10/instant-pot-dal-tadka.jpg"
},

{
    "name": "Tomato Rice",
    "ingredients": ["rice", "tomato"],
    "category": "Lunch",
    "time": "15 mins",
    "image": "https://spicyvegrecipes.com/wp-content/uploads/2020/08/KSP_0590-copy-2-min-min-scaled.jpeg"
},

# SNACKS

{
    "name": "Veg Pizza",
    "ingredients": ["pizza"],
    "category": "Snacks",
    "time": "15 mins",
    "image": "https://tse2.mm.bing.net/th/id/OIP.b1046Cdp-GRRQh0y3pUkKwHaLG?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"
},

{
    "name": "Pani Puri",
    "ingredients": ["pani"],
    "category": "Snacks",
    "time": "10 mins",
    "image": "https://i.pinimg.com/originals/6e/31/41/6e3141dede81a837b75f4d476272e0a5.jpg"
},

{
    "name": "Chocolate Cake",
    "ingredients": ["cake"],
    "category": "Snacks",
    "time": "2 mins",
    "image": "https://i.pinimg.com/originals/85/e5/e8/85e5e81828c7bf2685e067c0351fe915.png"
},

# DINNER

{
    "name": "Egg Curry",
    "ingredients": ["egg", "tomato"],
    "category": "Dinner",
    "time": "15 mins",
    "image": "https://www.bharatmasala.com/wp-content/uploads/2024/07/egg-curry-scaled.jpeg"
},

{
    "name": "Paneer Fry",
    "ingredients": ["paneer"],
    "category": "Dinner",
    "time": "20 mins",
    "image": "https://th.bing.com/th/id/OIP.avHTZlXY1kpgSmphTiSkPQHaFj?r=0&o=7rm=3&rs=1&pid=ImgDetMain&o=7&rm=3"
}

]

# ====================================
# LOGIN PAGE
# ====================================

@app.route('/')
def login():

    return render_template('login.html')

# ====================================
# SIGNUP PAGE
# ====================================

@app.route('/signup')
def signup():

    return render_template('signup.html')

# ====================================
# HOME PAGE
# ====================================

@app.route('/home')
def home():

    if 'user' not in session:
        return redirect('/')

    return render_template('index.html')

# ====================================
# CREATE ACCOUNT
# ====================================

@app.route('/create_account', methods=['POST'])
def create_account():

    username = request.form['username']
    password = request.form['password']

    with open("users.txt", "a") as file:

        file.write(f"{username},{password}\n")

    return redirect('/')

# ====================================
# LOGIN CHECK
# ====================================

@app.route('/login_check', methods=['POST'])
def login_check():

    username = request.form['username']
    password = request.form['password']

    with open("users.txt", "r") as file:

        users = file.readlines()

    for user in users:

        saved_username, saved_password = user.strip().split(",")

        if username == saved_username and password == saved_password:

            session['user'] = username

            return redirect('/home')

    return "Invalid Username or Password"

# ====================================
# LOGOUT
# ====================================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

# ====================================
# OCR + RECIPES
# ====================================

@app.route('/upload', methods=['POST'])
def upload_bill():

    if 'user' not in session:
        return redirect('/')

    file = request.files['bill']

    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file.filename
    )

    file.save(filepath)

    # OCR

    image = cv2.imread(filepath)

    extracted_text = pytesseract.image_to_string(image)

    lines = extracted_text.split('\n')

    grocery_data = []

    # EXTRACT ITEMS

    for line in lines:

        line = line.strip()

        if line == "":
            continue

        quantity_match = re.search(
            r'(\d+\s?(kg|g|gm|l|ml|pcs))',
            line.lower()
        )

        if quantity_match:

            quantity = quantity_match.group(1)

            item_name = line[:quantity_match.start()].strip()

            grocery_data.append({

                "item": item_name,
                "quantity": quantity

            })

    # INGREDIENTS

    ingredients = []

    for data in grocery_data:

        item = data['item'].lower()

        item = re.sub(r'[^a-zA-Z ]', '', item)

        words = item.split()

        for word in words:

            ingredients.append(word)

    ingredients = list(set(ingredients))

    # TABLE

    table_rows = ""

    for data in grocery_data:

        table_rows += f"""

        <tr>
            <td>{data['item']}</td>
            <td>{data['quantity']}</td>
        </tr>

        """

    # RECIPES

    categories = [
        "Breakfast",
        "Lunch",
        "Snacks",
        "Dinner"
    ]

    recipe_output = ""

    for category in categories:

        category_cards = ""

        for recipe in quick_recipes:

            if recipe["category"] == category:

                available = []
                missing = []

                for item in recipe["ingredients"]:

                    if item in ingredients:
                        available.append(item)
                    else:
                        missing.append(item)

                if len(available) >= 1:

                    category_cards += f"""

                    <div class="recipe-card">

                        <img src="{recipe['image']}">

                        <div class="recipe-content">

                            <h3>{recipe['name']}</h3>

                            <p class="time">
                                ⏱️ {recipe['time']}
                            </p>

                            <p>
                                <b>Available Ingredients:</b><br>
                                {", ".join(available)}
                            </p>

                            <p class="missing">
                                Missing:
                                {", ".join(missing)}
                            </p>

                        </div>

                    </div>

                    """

        if category_cards != "":

            recipe_output += f"""

            <h2 class="section-title">
                {category}
            </h2>

            <div class="recipe-grid">

                {category_cards}

            </div>

            """

    # FINAL PAGE

    return f"""

<html>

<head>

<title>GroChef</title>

<style>

body {{

    margin:0;
    padding:0;
    font-family:Arial;
    background:linear-gradient(to right,#dfe9f3,#ffffff);

}}

.header {{

    background:linear-gradient(to right,#43cea2,#185a9d);
    color:white;
    padding:30px;
    text-align:center;
    font-size:40px;
    font-weight:bold;

}}

.container {{

    width:90%;
    margin:auto;
    margin-top:30px;

}}

.logout {{

    float:right;
    text-decoration:none;
    background:red;
    color:white;
    padding:10px 20px;
    border-radius:10px;

}}

table {{

    width:100%;
    border-collapse:collapse;
    background:white;
    border-radius:15px;
    overflow:hidden;
    box-shadow:0px 5px 20px rgba(0,0,0,0.1);

}}

th {{

    background:#43cea2;
    color:white;
    padding:15px;

}}

td {{

    padding:15px;
    text-align:center;
    border-bottom:1px solid #ddd;

}}

.section-title {{

    margin-top:50px;
    color:#185a9d;
    font-size:40px;

}}

.recipe-grid {{

    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
    gap:25px;
    margin-top:20px;

}}

.recipe-card {{

    background:white;
    border-radius:20px;
    overflow:hidden;
    box-shadow:0px 5px 20px rgba(0,0,0,0.1);
    transition:0.3s;

}}

.recipe-card:hover {{

    transform:translateY(-10px);

}}

.recipe-card img {{

    width:100%;
    height:220px;
    object-fit:cover;

}}

.recipe-content {{

    padding:20px;

}}

.recipe-content h3 {{

    color:#185a9d;
    font-size:28px;

}}

.time {{

    color:green;
    font-weight:bold;

}}

.missing {{

    color:red;
    font-weight:bold;

}}

</style>

</head>

<body>

<div class="header">

🍽️ GroChef Smart Recipe Recommendations

</div>

<div class="container">

<a class="logout" href="/logout">

Logout

</a>

<h2 class="section-title">

🧾 Detected Grocery Items

</h2>

<table>

<tr>

<th>Ingredient</th>
<th>Quantity</th>

</tr>

{table_rows}

</table>

{recipe_output}

</div>

</body>

</html>

"""

# ====================================
# RUN APP
# ====================================

if __name__ == '__main__':

    app.run(debug=True)