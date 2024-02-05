from flask import Flask, send_file, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import datetime
import random


app = Flask(__name__)
app.secret_key = '9CNUzEv2cANumT8gBNSp5UkNY9RdUA7MyY9VL3FZV6wf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'
login_manager = LoginManager(app)
db = SQLAlchemy(app)
app.app_context().push()


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cat = db.Column(db.String(100), nullable=True)
    vendor = db.Column(db.Text, nullable=True)
    vendors = db.Column(db.Text, nullable=True)
    main_logo = db.Column(db.Text, nullable=False)
    logos = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(100), nullable=True)
    full_description = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    main_image = db.Column(db.Text, nullable=False)

    # сделать названия файлов кастомными, чтобы избежать ошибок (тк у всех будет logo.png logo.jpg и так далее)


class Vendors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.Text, nullable=True)


class Offers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    parent = db.Column(db.Integer, nullable=True)


class Requests(db.Model):    # offers but not allowed yet
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    photos = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=True)


class Suggestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    photos = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    accepted = db.Column(db.Boolean, nullable=True)


def rec(cats):
    result = []
    for i in cats:
        children = Categories.query.filter(Categories.parent == i.id).all()
        if children:
            result += [i] + rec(children)
        else:
            result += [i]
    return result


@app.route('/')
def index():
    products = Products.query.filter(Products.price > 0).order_by(Products.date.desc()).all()
    vendors_with_offers_ids = Offers.query.with_entities(Offers.vendor_id).all()
    vendors = set()
    for i in vendors_with_offers_ids:
        ven = Vendors.query.filter(Vendors.id == i[0]).first()
        vendors.add(ven)
    vendors = sorted(list(vendors), key=lambda x: (x.title, x.name, x.surname))
    basic = Categories.query.filter(Categories.parent == 0).all()
    cats = []
    all_cats = Categories.query.all()
    parents = [x[0] for x in Categories.query.filter(Categories.parent != 0).with_entities(Categories.parent).all()]
    cats_with_fa_plus = len(set(parents))
    for i in basic:
        children = Categories.query.filter(Categories.parent == i.id).all()
        if children:
            cats.append((i, 1))
        else:
            cats.append((i, 0))
    d = {}
    for i in all_cats:
        if i.parent in d:
            d[i.parent].append(i.id)
        else:
            d[i.parent] = [i.id]
    return render_template('index.html', cats=cats, data=products,
                           vendors=vendors, inners=cats_with_fa_plus, d=d)


@app.route('/get_cat_html', methods=['POST', 'GET'])
def get_cat_html():
    if request.method == 'POST':
        cat_id = int(request.form['cat_id'].lstrip('cat'))
        basic = Categories.query.filter(Categories.parent == cat_id).all()
        cats = []
        for i in basic:
            children = Categories.query.filter(Categories.parent == i.id).all()
            if children:
                cats.append((i, 1))
            else:
                cats.append((i, 0))
        return render_template('get_cat_html.html', cats=cats)
    return redirect('/')


@app.route('/product/<int:id>')
def product(id):
    return render_template('product.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/buy/<int:cart_id>')
def buy(cart_id):
    return render_template('buy.html')


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')

    if email and password:
        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if remember_me:
                login_user(user, remember=True)
            else:
                login_user(user, remember=False)

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect('/')
        else:
            flash('Адрес электронной почты и/или пароль введены неверно или пользователь не зарегистрирован в системе')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    surname = request.form.get('surname')
    phone = request.form.get('phone')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if password != password2:
            flash('Пароли не совпадают')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Users(phone=phone, email=email, password=hash_pwd, surname=surname, name=name, status='client')
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/legit_check')
def legit_check():
    return render_template('legit_check.html')


@app.route('/submit', methods=['POST', 'GET'])
@login_required
def submit():
    if current_user.status == 'admin' and request.method == 'POST':
        req_id = int(request.form['req_id'])
        this = Requests.query.filter(Requests.id == req_id).first()
        vendor_id = this.vendor_id
        product_id = this.product_id
        price = this.price
        new_offer = Offers(vendor_id=vendor_id, product_id=product_id, price=price)
        db.session.add(new_offer)
        Requests.query.filter(Requests.id == req_id).delete()
        db.session.commit()

        ids = [id[0] for id in Products.query.with_entities(Products.id).all()]
        for id in ids:
            prices_and_vendors = Offers.query.filter(Offers.product_id == id).with_entities(Offers.price,
                                                                                            Offers.vendor_id).all()
            vendors = list(set([x[1] for x in prices_and_vendors]))
            if not prices_and_vendors:
                continue
            min_price = min(prices_and_vendors, key=lambda x: x[0])
            main_vendor_id = min_price[1]
            vendor_info = Vendors.query.filter(Vendors.id == main_vendor_id).with_entities(Vendors.title, Vendors.name,
                                                                                           Vendors.logo).first()
            product_to_change = Products.query.filter(Products.id == id).first()
            product_to_change.price = min_price[0]
            if vendor_info[0]:
                product_to_change.vendor = vendor_info[0]
            else:
                product_to_change.vendor = vendor_info[1]
            product_to_change.main_logo = vendor_info[2]
            product_to_change.vendors = str(vendors)
            vendors.remove(main_vendor_id)
            random.shuffle(vendors)
            a = []
            for i in range(len(vendors)):
                if i >= 4:
                    break
                logo = Vendors.query.filter(Vendors.id == vendors[i]).with_entities(Vendors.logo).first()
                a.append(logo)
            logos = [x[0] for x in a]
            if not logos:
                db.session.commit()
                continue
            if len(logos) > 4:
                logos = logos[:4]
            product_to_change.logos = str(logos)
            db.session.commit()
        return 'nothing'
    return redirect('/')


@app.route('/reject', methods=['POST', 'GET'])
@login_required
def reject():
    if current_user.status == 'admin' and request.method == 'POST':
        req_id = int(request.form['req_id'])
        Requests.query.filter(Requests.id == req_id).delete()
        db.session.commit()
        return 'nothing'
    return redirect('/')


@app.route('/submit2', methods=['POST', 'GET'])
@login_required
def submit2():
    if current_user.status == 'admin' and request.method == 'POST':
        sug_id = int(request.form['sug_id'])
        this = Suggestions.query.filter(Suggestions.id == sug_id).first()
        this.accepted = True
        db.session.commit()
        print('submitted', this.id, this.title)
        return 'nothing'
    return redirect('/')


@app.route('/reject2', methods=['POST', 'GET'])
@login_required
def reject2():
    if current_user.status == 'admin' and request.method == 'POST':
        sug_id = int(request.form['sug_id'])
        Suggestions.query.filter(Suggestions.id == sug_id).delete()
        db.session.commit()
        return 'nothing'
    return redirect('/')


@app.after_request
def redirect_to_login(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)
    return response


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    ids = [id[0] for id in Products.query.with_entities(Products.id).all()]
    for id in ids:
        prices_and_vendors = Offers.query.filter(Offers.product_id == id).with_entities(Offers.price,
                                                                                        Offers.vendor_id).all()
        vendors = list(set([x[1] for x in prices_and_vendors]))
        if not prices_and_vendors:
            continue
        min_price = min(prices_and_vendors, key=lambda x: x[0])
        main_vendor_id = min_price[1]
        vendor_info = Vendors.query.filter(Vendors.id == main_vendor_id).with_entities(Vendors.title, Vendors.name,
                                                                                       Vendors.logo).first()
        product_to_change = Products.query.filter(Products.id == id).first()
        product_to_change.price = min_price[0]
        if vendor_info[0]:
            product_to_change.vendor = vendor_info[0]
        else:
            product_to_change.vendor = vendor_info[1]
        product_to_change.main_logo = vendor_info[2]
        vendors.remove(main_vendor_id)
        random.shuffle(vendors)
        a = []
        for i in range(len(vendors)):
            if i >= 4:
                break
            logo = Vendors.query.filter(Vendors.id == vendors[i]).with_entities(Vendors.logo).first()
            a.append(logo)
        logos = [x[0] for x in a]
        if not logos:
            db.session.commit()
            continue
        if len(logos) > 4:
            logos = logos[:4]
        product_to_change.logos = str(logos)

        db.session.commit()

    products = Products.query.order_by(Products.date.desc()).all()
    if current_user.status == 'vendor':
        vendor = Vendors.query.filter(Vendors.email == current_user.email).first()

    if request.method == 'POST':
        if 'new_title' in request.form:    # vendor_change form
            new_title = request.form['new_title']
            new_logo = request.files.get('new_logo')
            filename = secure_filename(new_logo.filename)
            if new_title != vendor.title:
                vendor.title = new_title
            if filename != vendor.logo and filename:
                new_logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                vendor.logo = filename
            db.session.commit()
        elif 'product_to_request' in request.form:  # vendor_trading form
            product_to_request = request.form['product_to_request'].replace('!@!@!', '"')
            price = request.form['price']
            photos = request.files.getlist('images[]')

            uploaded_images = []
            for file in photos:
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    uploaded_images.append(filename)

            new_request = Requests(product_id=int(product_to_request), price=float(price.replace(',', '.')),
                                   vendor_id=vendor.id, photos=str(uploaded_images), date=datetime.datetime.now())
            db.session.add(new_request)
            db.session.commit()

        elif 'product_title' in request.form:   # vendor_product form
            product_title = request.form['product_title']
            photos2 = request.files.getlist('images2[]')

            uploaded_images = []
            for file in photos2:
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    uploaded_images.append(filename)

            print(product_title, uploaded_images, sep='\n')
            new_request = Suggestions(title=product_title, vendor_id=vendor.id,
                                      photos=str(uploaded_images), date=datetime.datetime.now(), accepted=False)
            db.session.add(new_request)
            db.session.commit()

    if current_user.status == 'vendor':
        return render_template('account.html', user=current_user, data=products, vendor=vendor)
    if current_user.status == 'admin':
        reqs = Requests.query.order_by(Requests.date.desc()).all()
        reqs_data = []
        for req in reqs:
            ven = Vendors.query.filter(Vendors.id == req.vendor_id).first()
            prod = Products.query.filter(Products.id == req.product_id).first()
            reqs_data.append([ven, prod, req])
        suggestions = Suggestions.query.filter(Suggestions.accepted == 0).order_by(Suggestions.date.desc()).all()
        sug_data = []
        for sug in suggestions:
            ven = Vendors.query.filter(Vendors.id == sug.vendor_id).first()
            sug_data.append([ven, sug])
        return render_template('account.html', user=current_user,
                               data=products, reqs_data=reqs_data, sug_data=sug_data)
    return render_template('account.html', user=current_user, data=products)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if current_user.status != 'admin':
        return redirect('/')
    if request.method == 'POST':
        title = request.form['title']
        categories = request.form['categories'].split(',')
        cat = ' '.join(categories)
        description = request.form['description']
        full_description = request.form['full_description']
        images = request.files.getlist('images[]')
        main_image = request.files.get('main_image')
        hidden = int(request.form['hidden'])

        uploaded_images = []

        for file in images:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                uploaded_images.append(filename)

        if main_image:
            filename = secure_filename(main_image.filename)
            main_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_images.append(filename)
            main_image = main_image.filename
        else:
            main_image = uploaded_images[0]

        new_product = Products(title=title, cat=cat, description=description, price=-1,
                               full_description=full_description, main_image=secure_filename(main_image),
                               images=str(uploaded_images), date=datetime.datetime.now())
        db.session.add(new_product)
        if hidden:
            Suggestions.query.filter(Suggestions.id == hidden).delete()
        db.session.commit()
    suggest = Suggestions.query.filter(Suggestions.accepted == 1).all()
    cats = Categories.query.all()
    return render_template('create.html', sug=suggest, cats=cats)


@app.route('/get_suggested', methods=['POST', 'GET'])
@login_required
def get_suggested():
    if current_user.status != 'admin' or request.method != 'POST':
        return redirect('/')
    selected_sug = request.form['selected_sug']
    suggest = Suggestions.query.filter(Suggestions.id == selected_sug).first()
    return render_template('suggested_pics.html', suggested=suggest)


@app.route('/get_category', methods=['POST', 'GET'])
@login_required
def get_category():
    if current_user.status != 'admin' or request.method != 'POST':
        return redirect('/')
    cat_id = int(request.form['cat'].lstrip('s'))
    cat = Categories.query.filter(Categories.id == cat_id).first()
    cats = Categories.query.all()
    return render_template('get_category.html', cats=cats, selected_cat=cat)


@app.route('/category', methods=['POST', 'GET'])
@login_required
def category():
    if current_user.status != 'admin':
        return redirect('/')
    cats = Categories.query.all()
    if request.method == 'POST':
        parent = request.form['parent']
        title = request.form['title']
        new_cat = Categories(title=title, parent=parent)
        db.session.add(new_cat)
        db.session.commit()
    return render_template('category.html', cats=cats)


@app.route('/category_delete', methods=['POST', 'GET'])
@login_required
def category_delete():
    if current_user.status != 'admin':
        return redirect('/')
    cats = Categories.query.all()
    if request.method == 'POST':
        cat_id = int(request.form['parent'])
        children = Categories.query.filter(Categories.parent == cat_id).all()
        this = Categories.query.filter(Categories.id == cat_id).first()
        new_parent = this.parent
        for i in children:
            i.parent = new_parent
        Categories.query.filter(Categories.id == cat_id).delete()
        db.session.commit()
    return render_template('category_delete.html', cats=cats)


@app.route('/category_change', methods=['POST', 'GET'])
@login_required
def category_change():
    if current_user.status != 'admin':
        return redirect('/')
    cats = Categories.query.all()
    if request.method == 'POST':
        new_parent = int(request.form['parent'])
        new_title = request.form['title']
        cat_id = int(request.form['this'].lstrip('s'))
        this = Categories.query.filter(Categories.id == cat_id).first()
        this.title = new_title
        this.parent = new_parent
        db.session.commit()
    return render_template('category_change.html', cats=cats)


@app.route('/discard', methods=['POST', 'GET'])
@login_required
def discard():
    if current_user.status != 'admin' or request.method != 'POST':
        return redirect('/')
    return render_template('discard.html')


@app.route('/delete', methods=['POST', 'GET'])
@login_required
def delete():
    if current_user.status != 'admin':
        return redirect('/')
    if request.method == 'POST':
        product_to_delete = request.form['product_to_delete']
        print(product_to_delete)
        Products.query.filter(Products.id == int(product_to_delete)).delete()
        db.session.commit()
    products = Products.query.order_by(Products.date.desc()).all()
    return render_template('delete.html', data=products)


@app.route('/process_list', methods=['POST', 'GET'])
@login_required
def process_list():
    if current_user.status == 'admin' and request.method == 'POST':
        product_to_change = request.form['product_to_change']
        selected = Products.query.filter(Products.id == int(product_to_change)).first()
        return render_template('process_list.html', data=selected)
    return redirect('/')


@app.route('/change', methods=['POST', 'GET'])
@login_required
def change():
    if current_user.status != 'admin':
        return redirect('/')
    if request.method == 'POST':
        product_to_change = request.form['product_to_change']
        this = Products.query.filter(Products.id == int(product_to_change)).first()
        title = request.form['title']
        cat = request.form['cat']
        description = request.form['description']
        full_description = request.form['full_description']
        images = request.files.getlist('images[]')
        main_image = request.files.get('main_image')
        uploaded_images = []
        if images or main_image:
            for file in images:
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    uploaded_images.append(filename)
            if main_image:
                filename = secure_filename(main_image.filename)
                main_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                uploaded_images.append(filename)
                main_image = main_image.filename
            else:
                main_image = uploaded_images[0]
            this.main_image = secure_filename(main_image)
            this.images = str(uploaded_images)
        print(images, '\n', main_image)

        this.title = title
        this.cat = cat
        this.description = description
        this.full_description = full_description
        db.session.commit()
    products = Products.query.order_by(Products.date.desc()).all()
    return render_template('change.html', data=products)


@app.route('/become_a_seller', methods=['POST', 'GET'])
@login_required
def become_a_seller():
    if current_user.status != 'client':
        return redirect('/')
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        patronymic = request.form['patronymic']
        title = request.form['title']
        phone = request.form['phone']
        email = request.form['email']
        logo = request.files.get('logo')

        if logo:
            filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        vendor = Vendors(surname=surname, name=name, patronymic=patronymic,
                         title=title, phone=phone, email=email, logo=filename)

        user_to_change = Users.query.filter(Users.id == current_user.id).first()
        user_to_change.status = 'vendor'

        try:
            db.session.add(vendor)
            db.session.commit()
            return redirect('/')
        except:
            return 'Получилась ошибка'

    return render_template('become_a_seller.html')


if __name__ == '__main__':
    app.run(debug=True)
