import uvicorn as uvicorn

from app.main_hw import app

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
