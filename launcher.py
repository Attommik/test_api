import uvicorn
from server import server


if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=9998)
