#Python HTTP server for GraphQL.
from flask import Flask
from flask_graphql import GraphQLView
from QBE_CON import schema
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.add_url_rule('/QBE/', view_func=GraphQLView.as_view('graphql',
                 schema=schema, graphiql=True))
app.run(debug=True)
