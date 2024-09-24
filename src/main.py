'''
WikiGuess API entry point
'''

from flask import Flask

app = Flask(__name__)

@app.get("/")
def get_home():
    '''
    Stub for root API endpoint
    '''
    return "WikiGuess backend root"

if __name__ == "__main__":
    app.run(debug=True)
