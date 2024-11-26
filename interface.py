
from flask import Flask, request, jsonify, render_template, redirect, session, flash, url_for
from connection_to_db import Database, database_connection
from datetime import datetime

app = Flask(__name__, template_folder='templates')

app.secret_key = '12345'


@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in ['author1','admin','reader1']:
            flash('Ошибка: логин должен соответствовать задачам, выполняемым вами в рамках системы'
                  '. Возможные варианты:\n автор(author) - управление постами.\n Администратор'
                  '(admin) - управление блогами.\n Читатель(reader) - просмотр контента.', 'danger')
            return redirect(url_for('login'))

        query = "SELECT user_id FROM Users WHERE user_login = %s"
        user_data = Database.execute_query(query, params=(username,), fetch=True)
        user_id = user_data[0][0]
        session['user'] = username
        session['user_id'] = user_id
        session[
            'role'] = 'author' if username == 'author1' else 'admin' if username == 'admin' else 'reader'  # Определяем роль
        if username == 'author1':
            return redirect(url_for('author_menu'))
        elif username == 'admin':
            return redirect(url_for('admin_menu'))
        elif username == 'reader1':
            return redirect(url_for('reader_menu'))

    return render_template('login.html')


@app.route('/author_menu')
def author_menu():
    return render_template('author_menu.html')

@app.route('/admin_menu')
def admin_menu():
    return render_template('admin_menu.html')


@app.route('/admin_menu/create_blog', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_description = request.form['blog_description']
        blog_image = request.form['blog_image']
        admin_id = 1
        query = """
        INSERT INTO blogs (admin_id, blog_name, blog_description, blog_image)
        VALUES (%s, %s, %s, %s)
        """
        Database.execute_query(query, (admin_id, blog_name, blog_description, blog_image))
        return redirect(url_for('admin_menu'))
    return render_template('create_blog.html')


@app.route('/admin_menu/delete_blog', methods=['GET', 'POST'])
def delete_blog():
    if request.method == 'POST':
        blog_id = request.form['blog_id']
        query = "DELETE FROM Blogs WHERE blog_id = %s"
        Database.execute_query(query, (blog_id,))
        flash('Blog deleted successfully!', 'success')
        return redirect(url_for('admin_menu'))
    query = "SELECT blog_id, blog_name FROM Blogs"
    blogs = Database.execute_query(query, fetch=True)
    return render_template('delete_blog.html', blogs=blogs)


@app.route('/admin_menu/show_blog', methods=['GET', 'POST'])
def show_blog_posts():

    if request.method == 'POST':
        blog_id = request.form['blog_id']
        query_posts = """
            SELECT p.post_id, p.post_title, p.post_content, p.media_path, p.media_type, 
                   p.post_status, p.like_count, p.dislike_count, p.comments_count, u.user_login
            FROM Posts p
            LEFT JOIN Users u ON p.author_id = u.user_id
            WHERE p.blog_id = %s
            ORDER BY p.created_at DESC
            """
        posts = Database.execute_query(query_posts, (blog_id,), fetch=True)

        query_blog_name = "SELECT blog_name FROM Blogs WHERE blog_id = %s"
        blog_name = Database.execute_query(query_blog_name, (blog_id,), fetch=True)[0][0]

        return render_template('show_blog_posts.html', posts=posts, blog_name=blog_name)

    query_blogs = "SELECT blog_id, blog_name FROM Blogs"
    blogs = Database.execute_query(query_blogs, fetch=True)
    return render_template('select_blog2.html', blogs=blogs)

@app.route('/admin_menu/show_users', methods=['GET', 'POST'])
def show_users():
    with database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_login, user_role FROM Users WHERE user_role != 'admin'")
            users = cursor.fetchall()

    if request.method == 'POST':
        user_id = request.form['user_id']
        new_role = request.form['new_role']

        if new_role in ['author', 'reader']:
            Database.execute_query(
                "UPDATE Users SET user_role = %s WHERE user_id = %s", (new_role, user_id)
            )
            return redirect(url_for('show_users'))

    return render_template('show_users.html', users=users)


@app.route('/admin_menu/on_moderation', methods=['GET', 'POST'])
def moderating_posts():
    query = "SELECT * FROM Posts WHERE post_status = 'on moderation'"
    posts = Database.execute_query(query, fetch=True)

    return render_template('on_moderation_posts.html', posts=posts)


@app.route('/admin_menu/on_moderation/update_post', methods=['GET', 'POST'])
def update_post():
    if request.method == 'POST':
        post_id = request.form['post_id']
        post_title = request.form['post_title']
        post_content = request.form['post_content']
        media_path = request.form.get('media_path')
        media_type = request.form.get('media_type')

        update_query = """
            UPDATE Posts
            SET post_title = %s, post_content = %s, media_path = %s, media_type = %s
            WHERE post_id = %s
        """
        Database.execute_query(update_query, (post_title, post_content, media_path, media_type, post_id))

        return redirect(url_for('moderating_posts'))

    post_id = request.args.get('post_id')
    query = "SELECT post_id, post_title, post_content, media_path, media_type FROM Posts WHERE post_id = %s"
    post = Database.execute_query(query, (post_id,), fetch=True)

    if not post:
        return redirect(url_for('moderating_posts'))

    return render_template('edit_post.html', post=post[0])


@app.route('/admin_menu/on_moderation/publish_post', methods=['GET', 'POST'])
def publish_post():
    post_id = request.form.get('post_id')

    if not post_id:
        flash('Ошибка: ID поста не найдено.', 'danger')
        return redirect(url_for('moderating_posts'))

    update_query = """
        UPDATE Posts
        SET post_status = 'published'
        WHERE post_id = %s AND post_status = 'on moderation'
        """
    Database.execute_query(update_query, (post_id,))

    query = "SELECT * FROM Posts WHERE post_status = 'on moderation'"
    posts = Database.execute_query(query, fetch=True)

    return render_template('on_moderation_posts.html', posts=posts)


@app.route('/author_menu/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_content = request.form['post_content']
        media_path = request.form.get('media_path')
        media_type = request.form.get('media_type')
        blog_id = request.form['blog_id']
        user_nick = request.form['user_nick']

        query_user_id = "SELECT user_id FROM Users WHERE user_login = %s"
        user_id_result = Database.execute_query(query_user_id, (user_nick,), fetch=True)

        author_id = user_id_result[0][0]

        if not author_id:
            return redirect(url_for('login'))

        query = """
                INSERT INTO Posts (post_title, post_content, media_path, media_type, author_id, post_status, blog_id)
                VALUES (%s, %s, %s, %s, %s, 'on moderation', %s)
            """
        Database.execute_query(query, (post_title, post_content, media_path, media_type, author_id, blog_id))

        return redirect(url_for('author_menu'))

    query_blogs = "SELECT blog_id, blog_name FROM Blogs"
    blogs = Database.execute_query(query_blogs, fetch=True)

    return render_template('create_post.html', blogs=blogs)


@app.route('/author_menu/delete_post', methods=['GET', 'POST'])
def delete_post():
    if request.method == 'POST':
        post_id = request.form['post_id']
        query = "DELETE FROM Posts WHERE post_id = %s"
        Database.execute_query(query, (post_id,))
        return redirect(url_for('author_menu'))

    query = "SELECT post_id, post_title FROM Posts WHERE author_id = (SELECT user_id FROM Users WHERE user_login = %s)"
    posts = Database.execute_query(query, (session['user'],), fetch=True)
    return render_template('delete_post.html', posts=posts)



@app.route('/author_menu/published_posts')
def published_posts():
    query = "SELECT post_id, post_title, post_status FROM Posts WHERE author_id = (SELECT user_id FROM Users WHERE user_login = %s) AND post_status = 'published'"
    posts = Database.execute_query(query, (session['user'],), fetch=True)
    return render_template('published_posts.html', posts=posts)



@app.route('/author_menu/on_moderation_posts')
def on_moderation_posts():
    query = "SELECT post_id, post_title, post_status FROM Posts WHERE author_id = (SELECT user_id FROM Users WHERE user_login = %s) AND post_status = 'on moderation'"
    posts = Database.execute_query(query, (session['user'],), fetch=True)
    return render_template('on_moderation_posts.html', posts=posts)



@app.route('/select_blog', methods=['GET', 'POST'])
def select_blog():
    if request.method == 'POST':
        blog_id = request.form['blog_id']
        session['blog_id'] = blog_id
        return redirect(url_for('reader_menu'))

    query_blogs = "SELECT blog_id, blog_name FROM Blogs"
    blogs = Database.execute_query(query_blogs, fetch=True)
    return render_template('select_blog2.html', blogs=blogs)

@app.route('/reader_menu', methods=['GET', 'POST'])
def reader_menu():
    if request.args.get('select_blog') == 'true':
        session.pop('blog_id', None)
    blog_id = session.get('blog_id')

    if not blog_id:
        return redirect(url_for('select_blog'))

    query_posts = """
        SELECT p.post_id, p.post_title, p.post_content, p.media_path, p.media_type, 
               p.post_status, 
               COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'liked' THEN pr.user_id END), 0) AS like_count,
               COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'disliked' THEN pr.user_id END), 0) AS dislike_count,
               (SELECT COUNT(*) FROM Comments c WHERE c.post_id = p.post_id) AS comments_count,  -- Подсчет комментариев через подзапрос
               u.user_login
        FROM Posts p
        LEFT JOIN Users u ON p.author_id = u.user_id
        LEFT JOIN Posts_Reaction pr ON p.post_id = pr.post_id
        WHERE p.blog_id = %s
        GROUP BY p.post_id, u.user_login
        ORDER BY p.created_at DESC
    """
    posts = Database.execute_query(query_posts, (blog_id,), fetch=True)

    query_blog_name = "SELECT blog_name FROM Blogs WHERE blog_id = %s"
    blog_name = Database.execute_query(query_blog_name, (blog_id,), fetch=True)[0][0]
    user_role = session.get('role')

    return render_template('reader_menu.html', posts=posts, blog_name=blog_name, user_role=user_role)



def update_reaction_counts(post_id):
    query_like_count = """
    SELECT COUNT(*) FROM posts_reaction
    WHERE post_id = %s AND user_reaction = 'liked'
    """
    like_count_result = Database.execute_query(query_like_count, params=(post_id,), fetch=True)
    like_count = like_count_result[0][0]

    query_dislike_count = """
    SELECT COUNT(*) FROM posts_reaction
    WHERE post_id = %s AND user_reaction = 'disliked'
    """
    dislike_count_result = Database.execute_query(query_dislike_count, params=(post_id,), fetch=True)
    dislike_count = dislike_count_result[0][0]

    update_query = """
    UPDATE Posts
    SET like_count = %s, dislike_count = %s
    WHERE post_id = %s
    """
    Database.execute_query(update_query, params=(like_count, dislike_count, post_id))


@app.route('/like_or_dislike', methods=['POST'])
def like_or_dislike():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    post_id = request.form['post_id']
    reaction_type = request.form['reaction_type']
    blog_id = session.get('blog_id')

    if not blog_id:
        return redirect(url_for('reader_menu'))

    query_check = """
    SELECT user_reaction FROM posts_reaction 
    WHERE post_id = %s AND user_id = %s
    """
    reaction = Database.execute_query(query_check, params=(post_id, user_id), fetch=True)

    if reaction:
        current_reaction = reaction[0][0]
        if current_reaction == reaction_type:
            flash(f'You already {reaction_type} this post!', 'info')
        else:
            update_query = """
            UPDATE posts_reaction SET user_reaction = %s WHERE post_id = %s AND user_id = %s
            """
            Database.execute_query(update_query, params=(reaction_type, post_id, user_id))
    else:
        insert_query = """
        INSERT INTO posts_reaction (user_id, post_id, user_reaction)
        VALUES (%s, %s, %s)
        """
        Database.execute_query(insert_query, params=(user_id, post_id, reaction_type))

    update_reaction_counts(post_id)

    return redirect(url_for('reader_menu'))



@app.route('/reader_menu/comment_post', methods=['POST'])
def comment_post():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    post_id = request.form['post_id']
    comment_content = request.form['comment_content']

    if not comment_content.strip():
        return redirect(url_for('reader_menu'))

    insert_comment_query = """
            INSERT INTO Comments (user_id, post_id, comm_content)
            VALUES (%s, %s, %s)
        """
    Database.execute_query(insert_comment_query, (user_id, post_id, comment_content))

    increment_comment_count_query = """
            UPDATE Posts SET comments_count = comments_count + 1 WHERE post_id = %s
        """
    Database.execute_query(increment_comment_count_query, (post_id,))

    return redirect(url_for('reader_menu'))


@app.route('/reader_menu/search_post', methods=['GET'])
def search_post():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    blog_id = session.get('blog_id', None)
    if not query:
        return redirect(url_for('reader_menu'))

    search_query = """
            SELECT p.post_id, p.post_title, p.post_content, p.media_path, p.media_type, 
                   p.post_status, 
                   COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'liked' THEN pr.user_id END), 0) AS like_count,
                   COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'disliked' THEN pr.user_id END), 0) AS dislike_count,
                   COALESCE(COUNT(c.comment_id), 0) AS comments_count,
                   u.user_login
            FROM Posts p
            LEFT JOIN Users u ON p.author_id = u.user_id
            LEFT JOIN Posts_Reaction pr ON p.post_id = pr.post_id
            LEFT JOIN Comments c ON p.post_id = c.post_id
            WHERE (%s IS NULL OR p.blog_id = %s) 
              AND LOWER(p.post_title) LIKE LOWER(%s)
            GROUP BY p.post_id, u.user_login
            ORDER BY p.created_at DESC
        """

    search_term = f"%{query}%"
    posts = Database.execute_query(search_query, params=(blog_id, blog_id, search_term), fetch=True)

    if not posts:
        flash(f'No posts found for "{query}".', 'warning')

    return render_template('reader_menu.html', posts=posts, blog_name=f'Search results for "{query}"')




def get_reaction_count(post_id, reaction_type):
    query = """
        SELECT COUNT(*) FROM posts_reaction
        WHERE post_id = %s AND reaction_type = %s
    """
    result = Database.execute_query(query, (post_id, reaction_type), fetch=True)
    return result[0][0] if result else 0


@app.route('/post_details', methods=['POST'])
def post_details():
    post_id = request.form.get('post_id')

    if not post_id:
        return redirect(url_for('reader_menu'))

    query_post = """
        SELECT p.post_title, p.post_content, p.media_path, p.media_type, 
               p.like_count, p.dislike_count, p.comments_count, u.user_login, p.created_at
        FROM Posts p
        LEFT JOIN Users u ON p.author_id = u.user_id
        WHERE p.post_id = %s
    """
    post = Database.execute_query(query_post, (post_id,), fetch=True)

    if not post:
        return redirect(url_for('reader_menu'))

    post = post[0]

    query_tags = """
        SELECT t.tag_name
        FROM Tags t
        JOIN BlogTags bt ON t.tag_id = bt.tag_id
        JOIN Posts p ON bt.blog_id = p.blog_id
        WHERE p.post_id = %s
    """
    tags = Database.execute_query(query_tags, (post_id,), fetch=True)

    query_comments = """
        SELECT c.comm_content, u.user_login, c.creation_date
        FROM Comments c
        LEFT JOIN Users u ON c.user_id = u.user_id
        WHERE c.post_id = %s
        ORDER BY c.creation_date DESC
    """
    comments = Database.execute_query(query_comments, (post_id,), fetch=True)
    created_at = post[8]
    formatted_date = created_at.strftime('%Y-%m-%d %H:%M')

    formatted_comments = []
    for comment in comments:
        comment_date = comment[2]
        formatted_comment_date = comment_date.strftime('%Y-%m-%d %H:%M')
        formatted_comments.append({
            'content': comment[0],
            'user': comment[1],
            'created_at': formatted_comment_date
        })

    return render_template('post_details.html', post=post, tags=tags, comments=formatted_comments, formatted_date=formatted_date)


@app.route('/for_you', methods=['GET'])
def for_you():
    user_id = session.get('user_id')

    if not user_id:
        flash("Please log in to access personalized recommendations.", "danger")
        return redirect(url_for('login'))

    query_recommended_posts = """
        SELECT DISTINCT p.post_id, p.post_title, p.post_content, p.media_path, p.media_type, 
                        p.post_status, 
                        COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'liked' THEN pr.user_id END), 0) AS like_count,
                        COALESCE(COUNT(DISTINCT CASE WHEN pr.user_reaction = 'disliked' THEN pr.user_id END), 0) AS dislike_count,
                        COALESCE(COUNT(c.comment_id), 0) AS comments_count,
                        u.user_login
        FROM Posts p
        LEFT JOIN Blogs b ON p.blog_id = b.blog_id
        LEFT JOIN BlogTags bt ON b.blog_id = bt.blog_id
        LEFT JOIN Tags t ON bt.tag_id = t.tag_id
        LEFT JOIN Users u ON p.author_id = u.user_id
        LEFT JOIN Posts_Reaction pr ON p.post_id = pr.post_id
        LEFT JOIN Comments c ON p.post_id = c.post_id
        WHERE t.tag_id IN (
            SELECT t2.tag_id
            FROM Tags t2
            JOIN BlogTags bt2 ON t2.tag_id = bt2.tag_id
            JOIN Blogs b2 ON bt2.blog_id = b2.blog_id
            JOIN Posts p2 ON p2.blog_id = b2.blog_id
            JOIN Posts_Reaction pr2 ON p2.post_id = pr2.post_id
            WHERE pr2.user_id = %s AND pr2.user_reaction = 'liked'
        )
        GROUP BY p.post_id, u.user_login
        LIMIT 10
    """
    recommended_posts = Database.execute_query(query_recommended_posts, (user_id,), fetch=True)

    return render_template('section_for_you.html', recommended_posts=recommended_posts)


if __name__ == '__main__':
    app.run(debug=True)