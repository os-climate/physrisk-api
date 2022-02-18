from .app import create_app

app = create_app(debug=False)


@app.route("/")
def home():
    """The App home page."""

    return "Hello World !"


if __name__ == "__main__":
    import logging
    import os
    import sys

    # Add a logger
    a_logger = logging.getLogger()
    a_logger.setLevel(logging.DEBUG)
    output_file_handler = logging.FileHandler("output.log")
    stdout_handler = logging.StreamHandler(sys.stdout)
    a_logger.addHandler(output_file_handler)
    a_logger.addHandler(stdout_handler)

    address = "127.0.0.1"
    app.run(host=address, port=os.environ.get("FLASK_RUN_PORT", 8082), debug=os.environ.get("FLASK_DEBUG", False))
