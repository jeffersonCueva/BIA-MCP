from app.main import create_app, streamable_app

app = create_app()
streamable_app = streamable_app()
if __name__ == "__main__":
    app.run()
