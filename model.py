from abc import ABC, abstractmethod
from enum import Enum
import sqlite3


class ReactionType(Enum):
    LIKE = 'liked'
    DISLIKE = 'disliked'


class Role(Enum):
    ADMIN = 'admin'
    AUTHOR = 'author'
    READER = 'reader'


class Reaction:
    def __init__(self, reaction_type: ReactionType, user_id: int, post_id: int):
        self.typeOfReaction = reaction_type
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return f"Reaction(user_id={self.user_id}, post_id={self.post_id}, typeOfReaction={self.typeOfReaction})"

    def __eq__(self, other):
        return (self.user_id == other.user_id and self.post_id == other.post_id and self.typeOfReaction == other.typeOfReaction)


class User:
    def __init__(self, id: str, nickname: str, password: str, roles: list[Role]):
        self.id = id
        self.nickname = nickname
        self.password = password
        self.roles = roles if roles is not None else []


class TextComment:
    def __init__(self, text: str):
        self.text = text


class Comment:
    def __init__(self, id: int, text: TextComment, author: User, post_id: int):
        self.id = id
        self.text = text
        self.author = author
        self.post_id = post_id


class PostBody:
    def __init__(self, imageUrl: str, text: str):
        self.imageUrl = imageUrl
        self.text = text


class Post:
    def __init__(self, id: int, postBody: PostBody, author: User, reaction: list[Reaction], comm: list[Comment]):
        self.id = id
        self.postBody = postBody
        self.author = author
        self.reaction = reaction
        self.comm = comm if comm is not None else []


class Blog:
    def __init__(self, id: int, admin_id: int, name: str, posts: list[Post], users: list[User]):
        self.id = id
        self.admin_id = id
        self.name = name
        self.posts = posts if posts is not None else []
        self.users = users if users is not None else []


class IPostRepository(ABC):
    @abstractmethod
    def processPost(self, postBody: PostBody) -> Post:
        pass

    @abstractmethod
    def addPost(self, post: Post) -> None:
        pass

    @abstractmethod
    def deletePost(self, post: Post) -> None:
        pass

    @abstractmethod
    def updatePost(self, postNewBody: PostBody) -> None:
        pass

    @abstractmethod
    def getPost(self, post: Post) -> Post:
        pass


class PostRepository(IPostRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def processPost(self, post: Post) -> Post:
        query = """
        UPDATE Posts
        SET post_status = 'published'
        WHERE post_id = ?
        """
        with self._connect() as conn:
            cursor = conn.execute(query, (post.id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Post with ID {post.id} not found.")
            conn.commit()
        return self.getPost(post)

    def addPost(self, post: Post) -> None:
        query = """
        INSERT INTO Posts (post_title, post_content, media_path, media_type, post_status, author_id, blog_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                post.postBody.text,
                post.postBody.imageUrl,
                None,
                None,
                'pending',
                post.author.id,
                None
            ))
            conn.commit()

    def deletePost(self, post: Post) -> None:
        query = "DELETE FROM Posts WHERE post_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (post.id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Post with ID {post.id} not found.")
            conn.commit()

    def updatePost(self, post: Post) -> None:
        query = """
        UPDATE Posts
        SET post_content = ?, media_path = ?
        WHERE post_id = ?
        """
        with self._connect() as conn:
            conn.execute(query, (post.postBody.text, post.postBody.imageUrl, post.id))
            conn.commit()

    def getPost(self, post: Post) -> Post:
        query = "SELECT * FROM Posts WHERE post_id = ?"
        with self._connect() as conn:
            result = conn.execute(query, (post.id,)).fetchone()
            if not result:
                raise ValueError(f"Post with ID {post.id} not found.")

        reaction = self.getReactionsForPost(post.id)

        return Post(
            id=result[0],
            postBody=PostBody(imageUrl=result[2], text=result[1]),
            author=User(id=result[6], nickname="", password="", roles=[]),
            reaction=reaction,
            comm=[]
        )

    def getAllPosts(self) -> list[Post]:
        query = "SELECT * FROM Posts"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()

        return [
            Post(
                id=row[0],
                postBody=PostBody(imageUrl=row[2], text=row[1]),
                author=User(id=row[6], nickname="", password="", roles=[]),
                reaction=self.getReactionsForPost(row[0]),
                comm=[]
            )
            for row in rows
        ]

    def getReactionsForPost(self, post_id: int) -> list[Reaction]:
        query = "SELECT user_id, user_reaction FROM Posts_reaction WHERE post_id = ?"
        with self._connect() as conn:
            rows = conn.execute(query, (post_id,)).fetchall()
        reactions = [
            Reaction(user_id=row[0], post_id=post_id, reaction_type=ReactionType(row[1]))
            for row in rows
        ]
        return reactions


class IReactionRepository(ABC):
    @abstractmethod
    def addReaction(self, reaction: Reaction) -> Reaction:
        pass

    @abstractmethod
    def deleteReaction(self, reaction: Reaction) -> None:
        pass

    @abstractmethod
    def getReaction(self, reaction: Reaction) -> Reaction:
        pass


class ReactionRepository(IReactionRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def addReaction(self, reaction: Reaction) -> Reaction:
        query = """
        INSERT INTO Posts_reaction (user_id, post_id, user_reaction)
        VALUES (?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                reaction.user_id,
                reaction.post_id,
                reaction.typeOfReaction.value
            ))
            conn.commit()
        return reaction

    def deleteReaction(self, reaction: Reaction) -> None:
        query = "DELETE FROM Posts_reaction WHERE user_id = ? AND post_id = ?"
        with self._connect() as conn:
            conn.execute(query, (reaction.user_id, reaction.post_id))
            conn.commit()

    def getReaction(self, reaction: Reaction) -> Reaction:
        query = "SELECT * FROM Posts_reaction WHERE user_id = ? AND post_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (reaction.user_id, reaction.post_id))
            row = cursor.fetchone()
            if row:
                return Reaction(
                    user_id=row[0],
                    post_id=row[1],
                    reaction_type=ReactionType(row[2])
                )
            raise ValueError("Reaction not found.")


class IBlogRepository(ABC):
    @abstractmethod
    def getBlogName(self, blog_int: int) -> str:
        pass

    @abstractmethod
    def setBlogName(self, blog_id: int, new_name: str):
        pass

    @abstractmethod
    def addBlog(self, blog: Blog) -> None:
        pass

    @abstractmethod
    def deleteBlog(self, blog: Blog) -> None:
        pass


class BlogRepository(IBlogRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def getBlogName(self, blog_id: int) -> str:
        query = "SELECT blog_name FROM Blogs WHERE blog_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (blog_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            raise ValueError(f"Blog with ID {blog_id} not found.")

    def setBlogName(self, blog_id: int, new_name: str):
        query = "UPDATE Blogs SET blog_name = ? WHERE blog_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (new_name, blog_id))
            conn.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Blog with ID {blog_id} not found.")

    def addBlog(self, blog: Blog) -> None:
        query = """
        INSERT INTO Blogs (blog_name, admin_id, blog_description, blog_image)
        VALUES (?, ?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                blog.name,
                blog.admin_id,
                None,
                None
            ))
            conn.commit()

    def deleteBlog(self, blog: Blog) -> None:
        query = "DELETE FROM Blogs WHERE blog_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (blog.id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Blog with ID {blog.id} not found.")
            conn.commit()

    def setAdmin(self, blog_id: int, admin_name: str) -> None:
        query_find_admin = "SELECT user_id FROM Users WHERE user_login = ?"
        query_set_admin = "UPDATE Blogs SET admin_id = ? WHERE blog_id = ?"

        with self._connect() as conn:
            cursor = conn.execute(query_find_admin, (admin_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"User with name '{admin_name}' not found.")
            admin_id = result[0]

            conn.execute(query_set_admin, (admin_id, blog_id))
            conn.commit()

    def deleteAdmin(self, blog_id: int) -> None:
        query_remove_admin = "UPDATE Blogs SET admin_id = NULL WHERE blog_id = ?"

        with self._connect() as conn:
            conn.execute(query_remove_admin, (blog_id,))
            conn.commit()


class IAuthRepository(ABC):
    @abstractmethod
    def getUser(self, email: str) -> User:
        pass

    @abstractmethod
    def createUser(self, user: User) -> None:
        pass

    @abstractmethod
    def updateUser(self, userNew: User) -> None:
        pass

    @abstractmethod
    def deleteUser(self, user: User) -> None:
        pass


class AuthRepository(IAuthRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def getUser(self, email: str) -> User:
        query = "SELECT * FROM Users WHERE user_login = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (email,))
            row = cursor.fetchone()
            if row:
                roles = [Role(role) for role in row[3].split(',')]
                return User(id=row[0], nickname=row[1], password=row[2], roles=roles)
            raise ValueError(f"User with email {email} not found.")

    def createUser(self, user: User) -> None:
        query = """
        INSERT INTO Users (user_login, user_password, user_role)
        VALUES (?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (user.nickname, user.password, ','.join([role.value for role in user.roles])))
            conn.commit()

    def updateUser(self, userNew: User) -> None:
        query = """
        UPDATE Users
        SET user_login = ?, user_password = ?, user_role = ?
        WHERE user_id = ?
        """
        with self._connect() as conn:
            conn.execute(query, (userNew.nickname, userNew.password, ','.join([role.value for role in userNew.roles]), userNew.id))
            conn.commit()

    def deleteUser(self, user: User) -> None:
        query = "DELETE FROM Users WHERE user_id = ?"
        with self._connect() as conn:
            cursor = conn


class ICommentRepository(ABC):
    @abstractmethod
    def addComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def deleteComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def processComment(self, comment: Comment) -> Comment:
        pass


class CommentRepository(ICommentRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def addComment(self, comment: Comment) -> None:
        query = """
        INSERT INTO Comments (user_id, post_id, comm_content)
        VALUES (?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                comment.author.id,
                comment.post_id,
                comment.text.text
            ))
            conn.commit()

    def deleteComment(self, comment: Comment) -> None:
        query = "DELETE FROM Comments WHERE comment_id = ?"
        with self._connect() as conn:
            cursor = conn.execute(query, (comment.id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Comment with ID {comment.id} not found.")
            conn.commit()

    def processComment(self, comment: Comment) -> Comment:
        query = """
        UPDATE Comments
        SET comm_content = ?
        WHERE comment_id = ?
        """
        with self._connect() as conn:
            cursor = conn.execute(query, (comment.text.text, comment.id))
            conn.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Comment with ID {comment.id} not found.")
        return comment


class IPostService(ABC):
    @abstractmethod
    def processPost(self, postBody: PostBody) -> Post:
        pass

    @abstractmethod
    def addPost(self, post: Post) -> None:
        pass

    @abstractmethod
    def deletePost(self, post: Post) -> None:
        pass

    @abstractmethod
    def updatePost(self, postNewBody: PostBody) -> None:
        pass

    @abstractmethod
    def getPost(self, post: Post) -> Post:
        pass


class PostService(IPostService):
    def __init__(self):
        self.repository = None

    def SetPostRepository(self, repo: PostRepository):
        self.repository = repo

    def processPost(self, post: Post) -> Post:
        return self.repository.processPost(post)

    def addPost(self, post: Post) -> None:
        self.repository.addPost(post)

    def deletePost(self, post: Post) -> None:
        self.repository.deletePost(post)

    def updatePost(self, post: Post) -> None:
        self.repository.updatePost(post)

    def getPost(self, post: Post) -> Post:
        return self.repository.getPost(post)


class IReactionService(ABC):
    @abstractmethod
    def addReaction(self, reaction: Reaction) -> Reaction:
        pass

    @abstractmethod
    def deleteReaction(self, reaction: Reaction) -> None:
        pass

    @abstractmethod
    def getReaction(self, reaction: Reaction) -> Reaction:
        pass


class ReactionService(IReactionService):
    def __init__(self):
        self.repository = None

    def SetReactionRepository(self, repo: ReactionRepository):
        self.repository = repo

    def addReaction(self, reaction: Reaction) -> Reaction:
        return self.repository.addReaction(reaction)

    def deleteReaction(self, reaction: Reaction) -> None:
        self.repository.deleteReaction(reaction)

    def getReaction(self, reaction: Reaction) -> Reaction:
        return self.repository.getReaction(reaction)


class IBlogService(ABC):
    @abstractmethod
    def getBlogName(self, blog_int: int) -> str:
        pass

    @abstractmethod
    def setBlogName(self, blog_id: int, new_name: str):
        pass

    @abstractmethod
    def addBlog(self, blog: Blog) -> None:
        pass

    @abstractmethod
    def deleteBlog(self, blog: Blog) -> None:
        pass


class BlogService(IBlogService):
    def __init__(self):
        self.repository = None

    def SetBlogRepository(self, repo: BlogRepository):
        self.repository = repo

    def getBlogName(self, blog_int: int) -> str:
        return self.repository.getBlogName(blog_int)

    def setBlogName(self, blog_id: int, name: str) -> None:
        self.repository.setBlogName(blog_id, name)

    def addBlog(self, blog: Blog) -> None:
        self.repository.addBlog(blog)

    def deleteBlog(self, blog_id: int) -> None:
        self.repository.deleteBlog(blog_id)

    def setAdmin(self, name: str) -> None:
        self.repository.setAdmin(name)

    def deleteAdmin(self, name: str) -> None:
        self.repository.deleteAdmin(name)


class ICommentService(ABC):
    @abstractmethod
    def addComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def deleteComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def processComment(self, comment: Comment) -> None:
        pass


class CommentService(ICommentService):
    def __init__(self):
        self.repository = None

    def setCommentRepository(self, repo: CommentRepository):
        self.repository = repo

    def processComment(self, comment: Comment) -> None:
        self.repository.processComment(comment)

    def addComment(self, comment: Comment) -> None:
        self.repository.addComment(comment)

    def deleteComment(self, comment: Comment) -> None:
        self.repository.deleteComment(comment)


class IAuthService(ABC):
    @abstractmethod
    def register(self, user: User) -> bool:
        pass

    @abstractmethod
    def login(self, login: str, password: str) -> bool:
        pass

    @abstractmethod
    def updateUser(self, userNew: User) -> None:
        pass

    @abstractmethod
    def deleteUser(self, user: User) -> None:
        pass


class AuthService(IAuthService):
    def __init__(self):
        self._auth_repository = None

    def SetAuthRepository(self, repository: AuthRepository):
        self._auth_repository = repository

    def register(self, user: User) -> bool:
        try:
            self._auth_repository.createUser(user)
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self, login: str, password: str) -> bool:
        try:
            user = self._auth_repository.getUser(login)
            return user.password == password
        except ValueError:
            return False

    def updateUser(self, user: User) -> None:
        self._auth_repository.updateUser(user)

    def deleteUser(self, login: str) -> None:
        try:
            user = self._auth_repository.getUser(login)
            self._auth_repository.deleteUser(user)
        except ValueError:
            raise ValueError(f"Cannot delete: user with login '{login}' not found.")


class Platform:
    def __init__(self, db_path: str = "db.sql"):
        self.db_path = db_path
        self.services = {}
        self.repositories = {}

    def initRepositories(self) -> list:
        self.repositories = {
            "post_repository": PostRepository(self.db_path),
            "reaction_repository": ReactionRepository(self.db_path),
            "blog_repository": BlogRepository(self.db_path),
            "auth_repository": AuthRepository(self.db_path),
            "comment_repository": CommentRepository(self.db_path),
        }
        return list(self.repositories.values())

    def initServices(self) -> list:
        post_service = PostService()
        post_service.SetPostRepository(self.repositories["post_repository"])

        reaction_service = ReactionService()
        reaction_service.SetReactionRepository(self.repositories["reaction_repository"])

        blog_service = BlogService()
        blog_service.SetBlogRepository(self.repositories["blog_repository"])

        auth_service = AuthService()
        auth_service.SetAuthRepository(self.repositories["auth_repository"])

        comment_service = CommentService()
        comment_service.setCommentRepository(self.repositories["comment_repository"])

        self.services = {
            "post_service": post_service,
            "reaction_service": reaction_service,
            "blog_service": blog_service,
            "auth_service": auth_service,
            "comment_service": comment_service,
        }
        return list(self.services.values())

    def runPlatform(self):
        print("Initializing repositories...")
        repositories = self.initRepositories()
        print(f"Repositories initialized: {[type(repo).__name__ for repo in repositories]}")

        print("Initializing services...")
        services = self.initServices()
        print(f"Services initialized: {[type(service).__name__ for service in services]}")

        print("Platform is running. Ready to handle requests.")

if __name__ == "__main__":
    platform = Platform("db.sql")
    platform.runPlatform()
