from flask import  Flask , request , jsonify , make_response
from flask_sqlalchemy import SQLALchemy
import uuid
from werkzeug.security import generate_password_hash , check_password_hash
import jwt 
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] ='SQLITE:////mnt/c/Users/antho/documents/api_example/todo.db'

db = SQLALchemy(app)

class User(db.Model):
    id = db.column(db.Integer , primary_key = True)
    public_id = db.column(db.string(50) , unique = True)
    name = db.column(db.string(50))
    password = db.column(db.string(80))
    admin = db.column(db.Boolean)

class todo(db.model):
    id = db.column(db.Integer , primary_key= True)
    text = db.column(db.String(50))
    complete = db.column(db.Boolean)
    user_id = db.column(db.Integer)
def token_required(f):
    @wraps(f)
    def decorated(*args , **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers[x-access-token]
        if not token:
            return jsonify({'message' : 'Token is missing!'}) , 401
        try:
            data = jwt.decode(token , app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id =  data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}) , 401
        return f(current_user , *args , **kwargs)
    return decorated

@app.route('/user' , methods = ['GET'])
@token_required
def get_all_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function!'})
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.check_password_hash
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'user_data'})

@app.route('/user/<public_id>' , methods = ['GET'])
@token_required
def get_one_user(current_user , public_id):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function!'})
    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'message' : 'no user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.check_password_hash
    user_data['admin'] = user.admin
    return jsonify({'user' : user_data})

@app.route('/user' , methods = ['POST'])
@token_required
def create_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function!'})

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'] , method='sha256')
    new_user = User(public_Id = str(uuid.uuid4()) , name = data ['name'] , password = hashed_password ,admin=False )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'new user created!'})

@app.route('/user/<public_id>' , methods = ['PUT'])
@token_required
def promote_user(current_user , public_id):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function!'})

    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'message' : 'no user found!'})
    user.admin = True
    db.session.commit()
     
    return jsonify({'message' : 'the user has been promoted!'})

@app.route('/user/<user_id>' , methods = ['DELETE'])
@token_required
def delete_user(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'cannot perform that function!'})
    user = User.query.filter_by(public_id = public_id).first()

    if not user:
        return jsonify({'message' : 'no user found!'})
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'the user has been delted!'})

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify' , 401 , {'www-Authenticate' : 'Basic realm = "login required!"'})

    user = User.query.filter_by(name = auth.username).first()
    if not user:
        return make_response('could not verify' , 401 , {'www-Authenticate' : 'Basic realm = "login required!"'})

    if check_password_hash(user.password , auth.password):
        token = jwt.encode({'public_id' : user.public_id , 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)} , app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('could not verify' , 401 , {'www-Authenticate' : 'Basic realm = "login required!"'})

@app.route('/todo' , methods=['GET'])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id =current_user.id).all()
    output =[]
    for todo in todos:
        todo_data = {}
        todo_data = ['id'] = tado.id
        todo_data = ['text'] = todo.text
        dodo_data = ['complete'] = todo.complete
        output.append({'todos' : output})

    return jsonify({'todo' = output})

@app.route('/todo/<todo_id>' , methods=['GET'])
@token_required
def get_one_todo(current_user , todo_id):
    todo = Todo.query.filter_by(id = todo_id , user_id = current_user.id).First()

    if not todo:
        return jsonify({'message' : 'No todo found!'})
    todo_data = {}
    todo_data = ['id'] = tado.id
    todo_data = ['text'] = todo.text
    dodo_data = ['complete'] = todo.complete
    
    return jsonify(todo_data)

@app.route('/todo' , methods=['POST'])
@token_required
def create_todo(current_user):
    data = requst.git_json()
    new_todo = Todo(text = data ['text'] , complete = False , user_id = current_user.id)
    db.session.add(new_todo)
    db.session.commit() 
    return jsonify({'massage' : 'Todo created!'})

@app.route('/todo/<todo_id>' , methods=['PUT'])
@token_required
def create_todo(current_id , todo_id):
    todo = Todo.query.filter_by(id = todo_id , user_id = current_user.id).First()

    if not todo:
        return jsonify({'message' : 'No todo found!'})
    todo.complete = True
    db.session.commit()
    return jsonify({'message' : 'Todo item has been completed!'})

@app.route('/todo/<todo_id>' , methods=['DELETE'])
@token_required
def delete_todo(current_user , todo_id):
    todo = Todo.query.filter_by(id = todo_id , user_id = current_user.id).First()

    if not todo:
        return jsonify({'message' : 'No todo found!'})

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message' : 'Todo item deleted!'})

if __naqme__ == '__main__':
    app.run(debug=True)