import sqlite3
from datetime import date
import sys
import os


db_file = 'PostManager.db'

if os.path.exists(db_file):
    os.remove(db_file)


# Create and connect to the database
conn = sqlite3.connect("PostManager.db")

# Creating a cursor to execute the query
cursor = conn.cursor()

# Query to Create User Table
UserTableQuery = """
CREATE TABLE Users(
    UserID INTEGER PRIMARY KEY,
    Username TEXT NOT NULL,
    Email TEXT NOT NULL,
    Password TEXT NOT NULL,
    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""


# Query to Create Post Table

PostTableQuery = """
CREATE TABLE Posts (
    PostID INTEGER PRIMARY KEY,
    UserID INTEGER,
    Title TEXT NOT NULL,
    Content TEXT NOT NULL,
    PostDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
"""


# Query to Create Comment Table
CommentTableQuery = """
CREATE TABLE Comments (
    CommentID INTEGER PRIMARY KEY,
    PostID INTEGER,
    UserID INTEGER,
    CommentText TEXT NOT NULL,
    CommentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PostID) REFERENCES Posts(PostID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
"""

# Query to Create Categories
CategoriesTableQuery = """
CREATE TABLE Categories (
    CategoryID INTEGER PRIMARY KEY,
    CategoryName TEXT NOT NULL
);
"""

# Query to Create PostCategories
PostCategoriesTableQuery = """
CREATE TABLE PostCategories (
    PostID INTEGER,
    CategoryID INTEGER,
    PRIMARY KEY (PostID, CategoryID),
    FOREIGN KEY (PostID) REFERENCES Posts(PostID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);
"""

DummyUsers = """
-- Insert into Users table
INSERT INTO Users (Username, Email, Password) VALUES
    ('B Monish Moger', 'monish72003@gmai    l.com', 'password123'),
    ('DL Rameshwar', 'ramesh@gmail.com', 'lifeisstrange'),
    ('Dhruva S Nayak', 'dhruvasn@gmail.com', 'incorrectpassword'),
    ('Avanish Shenoy', 'ashenoy64@gmail.com', 'pass@123');
"""

DummyPostData="""
-- Insert into Posts table
INSERT INTO Posts (UserID, Title, Content) VALUES
    (1, 'A Culinary Adventure: Traditional Street Food Across Continents', 'Take your taste buds on a global tour! Join us in savoring the diverse flavors of traditional street food from Asia to South America. Discover the unique culinary delights that street vendors offer in bustling markets and vibrant alleys.'),
    (2, 'Exploring the Wonders of Underwater Photography', ' Dive into the mesmerizing world beneath the waves as we explore the art and techniques of capturing stunning underwater moments. From vibrant coral reefs to elusive marine life, discover the beauty that lies beneath the surface.'),
    (3, 'The Ultimate Guide to Urban Gardening', 'Turn your urban space into a green oasis! Learn the essentials of urban gardening, from choosing the right plants for small spaces to creative container gardening ideas. Embrace the joy of growing your own herbs, vegetables, and flowers in the heart of the city.'),
    (1, 'Mindful Living in a Fast-Paced World', 'In a world filled with constant noise and distractions, discover the art of mindful living. From meditation practices to cultivating gratitude, explore practical tips on how to bring balance and serenity into your daily life.');
"""

DummyComments="""
-- Insert into Comments table
INSERT INTO Comments (PostID, UserID, CommentText) VALUES
    (1, 2, 'I absolutely love trying street food from different countries! The diversity of flavors is incredible. Any recommendations for must-try street food?'),
    (1, 3, 'The variety of spices and ingredients used in street food is mind-blowing. Its like a global flavor journey in every bite!'),
    (2, 1, 'The beauty beneath the waves is truly awe-inspiring. Its amazing how photography can bring that world to those who may never experience it firsthand.');
"""

DummyCategories="""
-- Insert into Categories table
INSERT INTO Categories (CategoryName) VALUES
    ('Street Food'),
    ('Flavours'),
    ('Culinary Journeys'),
    ('Photography'),
    ('Ocean'),    
    ('City Life'),
    ('Gardening');
"""

DummyPostCat="""
-- Insert into PostCategories table
INSERT INTO PostCategories (PostID, CategoryID) VALUES
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 4),
    (2, 5),
    (3, 6),
    (3, 7);
"""

#creating all tables
try:
    cursor.execute(UserTableQuery)
    cursor.execute(PostTableQuery)
    cursor.execute(CommentTableQuery)
    cursor.execute(CategoriesTableQuery)
    cursor.execute(PostCategoriesTableQuery)
except Exception as e:
    print('Failed to create table due to following reason: ',e)
    sys.exit(0)
except:
    print('Failed to create table due to unknown reason: ')
    sys.exit(0)

#Inserting dummy data to the tabel
try:
    cursor.execute(DummyUsers)
    cursor.execute(DummyPostData)
    cursor.execute(DummyComments)
    cursor.execute(DummyCategories)
    cursor.execute(DummyPostCat)
    conn.commit()
except Exception as e:
    print('Failed to insert data due to following reason: ',e)
    sys.exit(0)
except:
    print('Failed  to insert data due to unknown reason: ')
    sys.exit(0)


def GetAllPostDetails(cursor):
    query = '''
        SELECT Posts.PostID, Posts.Title, Users.Username, Posts.PostDate, Posts.Content, COUNT(Comments.CommentID) AS CommentCount
        FROM Posts
        INNER JOIN Users ON Posts.UserID = Users.UserID
        LEFT JOIN Comments ON Posts.PostID = Comments.PostID
        GROUP BY Posts.PostID;
    '''
    cursor.execute(query)
    results = cursor.fetchall()

    for result in results:
        post_id, post_title, author_username, post_date, content, comment_count = result
        print(f"Title: {post_title}")
        print(f"Author: {author_username}\t Date: {post_date}")
        print(f"Content: {content}\n")
        print(f"Comment Count: {comment_count}\n")

        # Retrieve comments for the current post
        comment_query = '''
            SELECT Users.Username AS CommentedUser, Comments.CommentDate, Comments.CommentText
            FROM Comments
            INNER JOIN Users ON Comments.UserID = Users.UserID
            WHERE Comments.PostID = ?;
        '''

        cursor.execute(comment_query, (post_id,))
        comments = cursor.fetchall()

        for comment in comments:
            commented_user, comment_date, comment_text = comment
            print(f"Commented User: {commented_user}\t Date: {comment_date}")
            print(f"Comment: {comment_text}\n")

        print('-------------------------------------------------------')


def FindUsersWithNoPosts(cursor):
    query = """
        SELECT Users.UserID, Users.Username
        FROM Users
        LEFT JOIN Posts ON Users.UserID = Posts.UserID
        WHERE Posts.PostID IS NULL;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print("\nUsers with No Posts:")
    for result in results:
        user_id, username = result
        print(f"UserID: {user_id}, Username: {username}")

def GetMostActiveUsers(cursor):
    query = """
        SELECT Users.UserID, Users.Username, COUNT(Posts.PostID) AS PostCount
        FROM Users
        LEFT JOIN Posts ON Users.UserID = Posts.UserID
        GROUP BY Users.UserID
        ORDER BY PostCount DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print("\nUsers Ordered by Activity:")
    if results:
        for result in results:
            user_id, username, post_count = result
            print(f"UserID: {user_id}, Username: {username}, Post Count: {post_count}")
    else:
        print("No users found.")


def RetrievePostsWithCategory(cursor,category_name):

    query = f"""
        SELECT Posts.PostID, Posts.Title, Categories.CategoryName, Posts.Content
        FROM Posts
        INNER JOIN PostCategories ON Posts.PostID = PostCategories.PostID
        INNER JOIN Categories ON PostCategories.CategoryID = Categories.CategoryID
        LEFT JOIN Comments ON Posts.PostID = Comments.PostID
        WHERE Categories.CategoryName = ?;
    """

    cursor.execute(query, (category_name,))
    results = cursor.fetchall()

    print(f"\nPosts with Category: {category_name}")
    for result in results:
        post_id, title, category, content = result
        print(f"PostID: {post_id}, Title: {title}, Category: {category}")
        print(f"Content: {content}\n")

def FindUsersCommentedOnOwnPosts(cursor):
    query = """
        SELECT Users.UserID, Users.Username, Comments.CommentText
        FROM Users
        INNER JOIN Comments ON Users.UserID = Comments.UserID
        INNER JOIN Posts ON Users.UserID = Posts.UserID
        WHERE Comments.PostID = Posts.PostID;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    print("\nUsers who Commented on Their Own Posts:")
    for result in results:
        user_id, username, comment_text = result
        print(f"UserID: {user_id}, Username: {username}")
        print(f"Comment: {comment_text}\n")

def RetrievePostsWithAuthorsAndCommentCount(cursor):
    query = """
        SELECT 
            Posts.PostID,
            Posts.Title,
            Users.Username AS Author,
            COUNT(Comments.CommentID) AS CommentCount
        FROM Posts
        INNER JOIN Users ON Posts.UserID = Users.UserID
        LEFT JOIN Comments ON Posts.PostID = Comments.PostID
        GROUP BY Posts.PostID
        ORDER BY CommentCount DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print("\nPosts with Authors and Comment Counts:")
    for result in results:
        post_id, title, author, comment_count = result
        print(f"PostID: {post_id}, Title: {title}")
        print(f"Author: {author}, Comment Count: {comment_count}\n")


def RetrieveLatestPostsWithDetails(cursor,user_id):
    query = """
        SELECT 
            Posts.PostID,
            Posts.Title,
            Users.Username AS Author,
            Posts.PostDate,
            COUNT(Comments.CommentID) AS CommentCount
        FROM Posts
        INNER JOIN Users ON Posts.UserID = Users.UserID
        LEFT JOIN Comments ON Posts.PostID = Comments.PostID
        WHERE Users.UserID = ?
        GROUP BY Posts.PostID
        ORDER BY Posts.PostDate DESC
        LIMIT 1;
    """

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    print("\nLatest Post for User:")
    if result:
        post_id, title, author, post_date, comment_count = result
        print(f"PostID: {post_id}, Title: {title}")
        print(f"Author: {author}, Post Date: {post_date}, Comment Count: {comment_count}\n")
    else:
        print(f"No posts found for User ID {user_id}.")


if __name__=="__main__":
    
    os.system('cls')

    #Query retrives all posts
    # GetAllPostDetails(cursor)

    #Query to retrives users latest post
    # RetrieveLatestPostsWithDetails(cursor,1)
    
    #Query to retrive posts based on category
    RetrievePostsWithCategory(cursor,'Photography')

    #Query to get most active users
    # GetMostActiveUsers(cursor)

    #Query to find user with no post
    # FindUsersWithNoPosts(cursor)