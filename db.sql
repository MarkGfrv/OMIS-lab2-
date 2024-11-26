-- таблица с информацией о пользователях
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    user_login TEXT NOT NULL,
    user_password TEXT NOT NULL,
    user_role TEXT NOT NULL,
    CONSTRAINT user_unique UNIQUE (user_login, user_password),
    CONSTRAINT user_role_check CHECK (user_role IN ('admin', 'author', 'reader'))
);

-- таблица с информацией о блогах
CREATE TABLE Blogs (
    blog_id SERIAL PRIMARY KEY,
    admin_id INTEGER,
    blog_name TEXT NOT NULL,
    blog_description TEXT,
    blog_image TEXT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
    FOREIGN KEY (admin_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- таблица со всеми опубликованными постами
CREATE TABLE Posts (
    post_id SERIAL PRIMARY KEY,
    post_title TEXT NOT NULL,
    post_content TEXT NOT NULL,
    media_path TEXT,
    media_type TEXT,
    post_status TEXT NOT NULL DEFAULT 'pending',
    author_id INTEGER,
    blog_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    CONSTRAINT media_check CHECK (media_type IN ('image', 'video')),
    CONSTRAINT status_check CHECK (post_status IN ('published', 'pending', 'on moderation')),
    CONSTRAINT fk_user
    FOREIGN KEY (author_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_blog
    FOREIGN KEY (blog_id) REFERENCES Blogs(blog_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- таблица с понравившимися определенному пользователю постами
CREATE TABLE Posts_reaction (
    user_id INTEGER,
    post_id INTEGER,
    user_reaction TEXT NOT NULL DEFAULT 'skipped',
    CONSTRAINT unique_user_post_reaction UNIQUE (user_id, post_id),
    CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_post
    FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT reaction_check CHECK (user_reaction IN ('liked', 'disliked', 'skipped')),
    PRIMARY KEY (user_id, post_id)
);


-- таблица с комментариями к определенному посту
CREATE TABLE Comments (
    comment_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    post_id INTEGER,
    comm_content TEXT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_post
    FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- таблица с тегами
CREATE TABLE Tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name TEXT NOT NULL UNIQUE
);

-- промежуточная таблица для связи блогов с тегами (многие ко многим)
CREATE TABLE BlogTags (
    blog_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (blog_id, tag_id),
    CONSTRAINT fk_blog
    FOREIGN KEY (blog_id) REFERENCES Blogs(blog_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tag
    FOREIGN KEY (tag_id) REFERENCES Tags(tag_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Интерфейс для опубликованных постов
CREATE VIEW PublishedPosts AS
SELECT * FROM Posts
WHERE post_status = 'published';

-- Интерфейс для постов 'на модерации'
CREATE VIEW ModeratingPosts AS
SELECT * FROM Posts
WHERE post_status = 'on moderation';

-- Интерфейс для постов 'на редакции'
CREATE VIEW RedactionPosts AS
SELECT * FROM Posts
WHERE post_status = 'pending';

-- Интерфейс для всех понравившихся определенному пользователю постов
CREATE VIEW LikedPosts AS
SELECT post_title, post_content, like_count, dislike_count, comments_count, created_at
FROM Posts
JOIN Posts_reaction ON Posts.post_id = Posts_reaction.post_id
WHERE Posts_reaction.user_reaction = 'liked';

-- Интерфейс для получения всех тегов для конкретного блога
CREATE VIEW BlogTagsView AS
SELECT Blogs.blog_id, Blogs.blog_name, Tags.tag_name
FROM Blogs
JOIN BlogTags ON Blogs.blog_id = BlogTags.blog_id
JOIN Tags ON BlogTags.tag_id = Tags.tag_id;

-- Добавление пользователей
INSERT INTO Users (user_login, user_password, user_role) VALUES
('admin', 'password123', 'admin'),
('author1', 'mypassword', 'author'),
('reader1', 'letmein559', 'reader'),
('reader2', 'read123', 'reader');

-- Добавление блогов
INSERT INTO Blogs (admin_id, blog_name, blog_description, blog_image) VALUES
(1, 'Tech Insights', 'A blog about the latest in technology.', 'tech.jpg'),
(1, 'Travel Diaries', 'Exploring the world, one place at a time.', 'travel.jpg');

-- Добавление постов
INSERT INTO Posts (post_title, post_content, media_path, media_type, post_status, author_id, blog_id) VALUES
('Latest AI Trends', 'Discussion on the latest in artificial intelligence.', 'ai.jpg', 'image', 'published', 2, 1),
('Top 10 Beaches', 'A list of the best beaches around the world.', NULL, NULL, 'published', 2, 2),
('Quantum Computing Basics', 'Introduction to quantum computing.', 'quantum.mp4', 'video', 'on moderation', 2, 1),
('Best Travel Apps', 'Apps every traveler should have.', 'apps.jpg', 'image', 'pending', 2, 2);



-- Добавление тегов
INSERT INTO Tags (tag_name) VALUES
('Technology'),
('AI'),
('Travel'),
('Beaches'),
('Quantum Computing');

-- Связь блогов с тегами
INSERT INTO BlogTags (blog_id, tag_id) VALUES
(1, 1), -- Tech Insights -> Technology
(1, 2), -- Tech Insights -> AI
(1, 5), -- Tech Insights -> Quantum Computing
(2, 3), -- Travel Diaries -> Travel
(2, 4); -- Travel Diaries -> Beaches


-- Функция для предотвращения добавления второго лайка
CREATE OR REPLACE FUNCTION prevent_multiple_likes()
RETURNS TRIGGER AS $$
BEGIN
    -- Проверяем, есть ли уже лайк от этого пользователя на этот пост
    IF EXISTS (
        SELECT 1
        FROM Posts_reaction
        WHERE user_id = NEW.user_id AND post_id = NEW.post_id AND user_reaction = 'liked'
    ) THEN
        -- Если лайк уже есть, выбрасываем исключение
        RAISE EXCEPTION 'User can only like a post once.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для предотвращения добавления второго лайка
CREATE TRIGGER prevent_multiple_likes_trigger
BEFORE INSERT ON Posts_reaction
FOR EACH ROW
EXECUTE FUNCTION prevent_multiple_likes();

