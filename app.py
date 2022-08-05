# Import the Flask Dependency
from flask import Flask

# Create a new Flask instance called `app`,
# being sure to pass Python **magic method** `__name__`
app = Flask(__name__)

# Define the **root** (highest level of hierarchy) starting point
@app.route("/")
def hello_world():
    return '(: Hello world :)'

# Define what to do at /contact route
@app.route("/contact")
def contact():
    print("Server received request for 'Contact' page...")
    return "...yet to be implemented!"

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)