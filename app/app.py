from flask import Flask, jsonify, request, Response, render_template
import sqlite3

app = Flask(__name__)

#Location of the db on the docker container.
DATABASE = '/mount/database.db'

def connect_db():
    return sqlite3.connect(DATABASE)


# Class used to represent comments.
class Comment():
    # Comments should only be initialized with comment_ids if they are coming from the database.
    def __init__(self, the_comment, likes=0, comment_id=None):
        self.comment = the_comment
        self.likes = likes
        self.id = comment_id

    # Increment likes by one.
    def increment_likes(self):
        self.likes += 1

    # Decrement likes by one. We return the status code 403 if there are no more like to remove.
    def decrement_likes(self):
        if self.likes <= 0:
            return 403
        else:
            self.likes -= 1
            return 204

    # Adds the comment to the db, and sets the self.id param based on the response.
    def add_to_db(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''INSERT INTO COMMENTS(comment, likes) VALUES(?, ?)''', (self.comment, self.likes))
        conn.commit()
        comment_id = cur.lastrowid
        self.id = comment_id
        return comment_id

    # Updates the likes value of the database, which is the only mutable value of the comment.
    def update_db(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute((f"UPDATE COMMENTS SET likes={self.likes} WHERE generated_id={self.id};"))
        conn.commit()

    def to_dict(self):
        return {"comment": self.comment, "likes": self.likes, "comment_id": self.id}

    # Takes a comment id and deletes the comment with that id from the db.
    @staticmethod
    def delete_from_db(comment_id):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM COMMENTS WHERE generated_id={comment_id}")
        conn.commit()
        return True

    # Creates a comment from the db based on the comment_id given
    @staticmethod
    def get_from_db(comment_id):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM COMMENTS WHERE generated_id={comment_id}")
        row_array = cur.fetchall()
        try:
            row = row_array[0]
        except IndexError:
            return None
        return Comment(row[1], row[2], row[0])

    # Returns an array of all comments present in the db
    @staticmethod
    def get_all_from_db():
        conn=connect_db()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM COMMENTS")
        rows = cur.fetchall()
        comment_array = []
        for row in rows:
            a_comment = Comment(row[1], row[2], row[0])
            comment_array.append(a_comment)
        return comment_array

# Helper function called from all functions that can break when the comment_id is not valid
def no_comment_for_id(comment_id):
    return f"No comment found for id {comment_id}", 404

# The main page is a static readme file
@app.route('/')
def main_page():
    return render_template("readme.html")

@app.route('/readme')
def read_me():
    return main_page()

# For /comment
# GET:
#   Returns a dict of all comments
# POST:
#   Expects a json {"comment": "TEXT"} where TEXT is the text of the comment
@app.route('/comment', methods=["GET","POST"])
def comment():
    if request.method == "POST":
        comment_text = request.json.get("comment")
        the_comment = Comment(comment_text)
        the_comment.add_to_db()
        return_dict = {"response": "Comment Created", "comment_dict": the_comment.to_dict()}
        return jsonify(return_dict), 201
    elif request.method == "GET":
        comment_array = Comment.get_all_from_db()
        comments_dict_array = []
        for a_comment in comment_array:
            comments_dict_array.append(a_comment.to_dict())
        return_dict = {"comments": comments_dict_array}
        return jsonify(return_dict), 200
    else:
        return Response('Method Not Allowed, Accepts GET and POST',  status=405)


@app.route('/comment/<comment_id>', methods=["GET", "DELETE"])
def comment_id_page(comment_id):
    # If get, we return a json of the comment
    if request.method == "GET":
        the_comment = Comment.get_from_db(comment_id)
        if not the_comment:
            return no_comment_for_id(comment_id)
        return_dict = the_comment.to_dict()
        return jsonify(return_dict), 200
    # If delete, we try to delete the comment and always return 204
    elif request.method == "DELETE":
        Comment.delete_from_db(comment_id)
        return "", 204
    else:
        return Response('Method Not Allowed, Accepts GET and DELETE',  status=405)



@app.route('/comment/<comment_id>/like', methods=["POST"])
def like_comment(comment_id):
    the_comment = Comment.get_from_db(comment_id)
    if not the_comment:
        return no_comment_for_id(comment_id)
    the_comment.increment_likes()
    the_comment.update_db()
    return "", 204


@app.route('/comment/<comment_id>/unlike', methods=["POST"])
def unlike_comment(comment_id):
    the_comment = Comment.get_from_db(comment_id)
    if not the_comment:
        return no_comment_for_id(comment_id)
    unlike_response = the_comment.decrement_likes()
    the_comment.update_db()
    if unlike_response == 204:
        return_value = ""
    else:
        return_value = {"response": "No more likes to remove", "comment_dict": the_comment.to_dict()}
    return jsonify(return_value), unlike_response


# Function called when flask is started, will create a sqlite db if one is not already present.
def create_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE COMMENTS ([generated_id] INTEGER PRIMARY KEY AUTOINCREMENT, comment TEXT, likes INTEGER)")
        print("Created table comments", flush=True)
    except:
        print("Table Comments already exists", flush=True)


if __name__ == '__main__':
    create_db()
    app.run(debug=True, host='0.0.0.0')