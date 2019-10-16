import sys
from flask import Flask, render_template , request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgres://postgres:psql@localhost:5432/pythontutorial';
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app);
migrate = Migrate(app, db)


#Child's Model
class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.Text, nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
  
  def __ref__(self):
    return f'<Todo {self.id} {self.description}, {self.completed}>'
# db.create_all()

#Parent model
class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name =  db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True)

  def __ref__(self):
    return f'<TodoList {self.id} {self.name}>'

order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Order(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  status = db.Column(db.String(), nullable=False)
  products = db.relationship('Product', secondary=order_items,
      backref=db.backref('orders', lazy=True))

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
    
@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False;
  body = {}
  try:
    description = request.get_json()['description'];
    list_id = request.get_json()['list_id'];
    todo = Todo(description=description, list_id=list_id);
    db.session.add(todo);
    db.session.commit()
    body['description'] = todo.description
    print(jsonify(body))
  except:
    error = True;
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      return jsonify(body) 

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete-todo', methods=['DELETE'])
def delete_todo(todo_id):
  print(todo_id)
  try:
    todo = Todo.query.get(todo_id) 
    db.session.delete(todo) 
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': 'Todo successfully deleted'})


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html',
  lists=TodoList.query.all(),
  active_list=TodoList.query.get(list_id),
  todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=1))