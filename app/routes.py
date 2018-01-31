from app import app, db
from flask import render_template, url_for, flash, redirect, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, RecipeForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, UserTokens, Recipe
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    recipes = current_user.followed_recipes().paginate(
        page, app.config['RECIPES_PER_PAGE'], False)
    next_url = url_for('index', page=recipes.next_num) \
               if recipes.has_next else None
    prev_url = url_for('index', page=recipes.prev_num) \
               if recipes.has_prev else None
    return render_template('index.html',
                           title='%s - Receptsamling' % current_user.username,
                           recipes=recipes.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           headline='Startsida')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() or\
               User.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Felaktigt användarnamn eller lösenord')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',
                           title='Logga in',
                           form=form,
                           headline='Logga in')

@app.route('/register/<token>', methods=['GET','POST'])
def register(token=None):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user_token = UserTokens.query.filter_by(token_string=token).first()
    if not user_token:
        flash('Du måste ha en inbjudan för att kunna registrera dig.')
        flash('Klicka på länken i ditt inbjudnings-mail för att registrera dig.')
        return redirect(url_for('index'))
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data,
                        email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.delete(user_token)
            db.session.commit()
            flash('Grattis! Du är registrerad som användare.')
            return redirect(url_for('login'))
    return render_template('register.html',
                           title='Registrering',
                           form=form,
                           headline='Registrera användare')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.filter_by(author=user).paginate(
        page, app.config['RECIPES_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=recipes.next_num) \
               if recipes.has_next else None
    prev_url = url_for('user', username=user.username, page=recipes.prev_num) \
               if recipes.has_prev else None
    return render_template('user.html',
                           user=user,
                           recipes=recipes.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           headline='Profil')

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Ditt användarnamn har sparats som {}'.format(current_user.username))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html',
                           title='Redigera profil',
                           form=form,
                           headline='Redigera profil')

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Användare {} hittades inte.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Du kan inte fökja dig själv!')
        redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Du följer {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Användare {} hittades inte.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Du kan inte sluta följa dig själv')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Du har slutat följa {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/following/<username>')
@login_required
def following(username=None):
    user = User.query.filter_by(username=username).first()
    following = user.followed.all()
    return render_template('follows.html',
                           headline='Användare som {} följer'.format(user.username),
                           follows=following)

@app.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    followers = user.followers.all()
    return render_template('follows.html',
                           headline='Användare som {} följer'.format(user.username),
                           follows=followers)

@app.route('/new_recipe', methods=['GET','POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(name=form.name.data,
                        author=current_user,
                        notes=form.notes.data)
        db.session.add(recipe)
        db.session.commit()
        flash('Receptet har sparats.')
        return redirect(url_for('recipe', recipe_id=recipe.id))
    return render_template('new_recipe.html',
                           form=form,
                           headline='Nytt recept')

@app.route('/copy_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def copy_recipe(recipe_id):
    original = Recipe.query.get(int(recipe_id))
    form = RecipeForm()
    form.name.data = original.name
    form.notes.data = original.notes
    if form.validate_on_submit():
        copy = Recipe(name=request.form.get('name',None),
                      notes=request.form.get('notes',None),
                      user_id=current_user.id,
                      original_author_id=original.author.id,
                      original_recipe_id=original.id)
        db.session.add(copy)
        db.session.commit()
        flash('Receptet har sparats')
        return redirect(url_for('recipe', recipe_id=copy.id))
    return render_template('edit_recipe.html',
                           title='Spara en kopia',
                           headline='Spara en kopia',
                           form=form,
                           recipe=original)

@app.route('/recipe/<recipe_id>')
@login_required
def recipe(recipe_id=None):
    recipe = Recipe.query.get(int(recipe_id))
    return render_template('recipe.html',
                           recipe=recipe,
                           headline='Recept')

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.order_by(Recipe.timestamp.desc()).paginate(
        page, app.config['RECIPES_PER_PAGE'], False)
    next_url = url_for('explore', page=recipes.next_num) \
               if recipes.has_next else None
    prev_url = url_for('explore', page=recipes.prev_num) \
               if recipes.has_prev else None
    return render_template('index.html',
                           title='Utforska',
                           recipes=recipes.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           headline='Utforska')

@app.route('/edit_recipe/<recipe_id>', methods=['GET','POST'])
@login_required
def edit_recipe(recipe_id=None):
    recipe = Recipe.query.get(int(recipe_id))
    if not recipe.author == current_user:
        flash('Du kan bara redigera dina egna recept')
        return redirect(url_for('recipe', recipe_id=recipe_id))
    form = RecipeForm()
    form.name.data = recipe.name
    form.notes.data = recipe.notes
    if form.validate_on_submit():
        recipe.name = request.form.get('name', None)
        recipe.notes = request.form.get('notes', None)
        db.session.commit()
        flash('Receptet har redigerats.')
        return redirect(url_for('recipe', recipe_id=recipe_id))
    return render_template('edit_recipe.html',
                           title='Redigera',
                           recipe=recipe,
                           headline='Redigera recept',
                           form=form)
