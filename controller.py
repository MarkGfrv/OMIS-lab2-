from abc import ABC, abstractmethod
from enum import Enum
from classes import User, Role, ReactionType, Reaction, TextComment, Comment, PostBody, Post, Blog, IPostRepository, IAuthRepository, ICommentRepository, IReactionRepository, IBlogRepository, IPostService, IReactionService, IBlogService, IAuthService, ICommentService, PostService, ReactionService, BlogService, AuthService, CommentService, PostRepository, ReactionRepository, BlogRepository, AuthRepository, CommentRepository


class IBlogController(ABC):
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

class BlogController(IBlogController):
    def __init__(self):
        self.service = None

    def setBlogService(self, service: BlogService):
        self.service = service

    def getBlogName(self, blog_id: int) -> str:
        blog = self.service.getBlog(blog_id)
        if blog:
            return blog.name
        else:
            raise ValueError(f"Blog with ID {blog_id} not found")

    def setBlogName(self, blog_id: int, new_name: str) -> None:
        blog = self.service.getBlog(blog_id)
        if blog:
            blog.name = new_name
            self.service.updateBlog(blog)
        else:
            raise ValueError(f"Blog with ID {blog_id} not found")

    def addBlog(self, blog: Blog) -> None:
        self.service.addBlog(blog)

    def deleteBlog(self, blog_id: int) -> None:
        blog = self.service.getBlog(blog_id)
        if blog:
            self.service.deleteBlog(blog)
        else:
            raise ValueError(f"Blog with ID {blog_id} not found")

class IPostController(ABC):
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
    def updatePost(self, post_id: int, postNewBody: PostBody) -> None:
        pass

    @abstractmethod
    def getPost(self, post: Post) -> Post:
        pass

class PostController(IPostController):
    def __init__(self):
        self.service = None

    def setPostService(self, service: PostService):
        self.service = service

    def processPost(self, postBody: PostBody) -> Post:
        post = self.service.createPost(postBody)
        return post

    def addPost(self, post: Post) -> None:
        self.service.addPost(post)

    def deletePost(self, post_id: int) -> None:
        post = self.service.getPost(post_id)
        if post:
            self.service.deletePost(post)
        else:
            raise ValueError(f"Post with ID {post_id} not found")

    def updatePost(self, post_id: int, new_body: PostBody) -> None:
        post = self.service.getPost(post_id)
        if post:
            post.body = new_body
            self.service.updatePost(post)
        else:
            raise ValueError(f"Post with ID {post_id} not found")

    def getPost(self, post_id: int) -> Post:
        return self.service.getPost(post_id)


class IReactionController(ABC):
    @abstractmethod
    def addReaction(self, reaction: Reaction) -> Reaction:
        pass

    @abstractmethod
    def deleteReaction(self, reaction: Reaction) -> None:
        pass

    @abstractmethod
    def getReaction(self, reaction: Reaction) -> Reaction:
        pass


class ReactionController(IReactionController):
    def __init__(self):
        self.service = None

    def setReactionService(self, service: PostService):
        self.service = service

    def addReaction(self, reaction: Reaction) -> None:
        self.service.addReaction(reaction)

    def deleteReaction(self, reaction_id: int) -> None:
        reaction = self.service.getReaction(reaction_id)
        if reaction:
            self.service.deleteReaction(reaction)
        else:
            raise ValueError(f"Reaction with ID {reaction_id} not found")

    def getReaction(self, reaction: Reaction) -> Reaction:
        return self.service.getReaction(reaction)


class ICommentController(ABC):
    @abstractmethod
    def addComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def deleteComment(self, comment: Comment) -> None:
        pass

    @abstractmethod
    def processComment(self, comment_id: int, commentText: TextComment) -> None:
        pass


class CommentController(ICommentController):
    def __init__(self):
        self.service = None

    def setCommentService(self, service: PostService):
        self.service = service

    def addComment(self, comment: Comment) -> None:
        self.service.addComment(comment)

    def deleteComment(self, comment_id: int) -> None:
        comment = self.service.getComment(comment_id)
        if comment:
            self.service.deleteComment(comment)
        else:
            raise ValueError(f"Comment with ID {comment_id} not found")

    def processComment(self, comment_id: int, new_text: TextComment) -> None:
        comment = self.service.getComment(comment_id)
        if comment:
            comment.text = new_text
            self.service.updateComment(comment)
        else:
            raise ValueError(f"Comment with ID {comment_id} not found")


class IAuthController(ABC):
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


class AuthController(IAuthController):
    def __init__(self):
        self.service = None

    def setAuthService(self, service: PostService):
        self.service = service

    def register(self, user: User) -> bool:
        return self.service.register(user)

    def login(self, login: str, password: str) -> bool:
        return self.service.login(login, password)

    def updateUser(self, userNew: User) -> None:
        self.service.updateUser(userNew)

    def deleteUser(self, user_id: int) -> None:
        user = self.service.getUser(user_id)
        if user:
            self.service.deleteUser(user)  # Удаление пользователя
        else:
            raise ValueError(f"User with ID {user_id} not found")


class MainController:
    def __init__(self):
        self.controllers = {}

    def initControllers(self, services: dict) -> list:
        blog_controller = BlogController()
        blog_controller.setBlogService(services.get("blog_service"))
        self.controllers["blog_controller"] = blog_controller

        post_controller = PostController()
        post_controller.setPostService(services.get("post_service"))
        self.controllers["post_controller"] = post_controller

        reaction_controller = ReactionController()
        reaction_controller.setReactionService(services.get("reaction_service"))
        self.controllers["reaction_controller"] = reaction_controller

        comment_controller = CommentController()
        comment_controller.setCommentService(services.get("comment_service"))
        self.controllers["comment_controller"] = comment_controller

        auth_controller = AuthController()
        auth_controller.setAuthService(services.get("auth_service"))
        self.controllers["auth_controller"] = auth_controller

        return list(self.controllers.values())

