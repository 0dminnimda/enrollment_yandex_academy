from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/red")
def read_sus():
    return "Red is sus af, vote 'em out!"


@app.get("/airspeed_of_a_fully_laden_swallow/{speed}")
def read_item(speed: int):
    answer = "Wrong!!"
    if speed == 40:
        answer = "Yes!! 40 kilometers per hour"
    elif speed == 11:
        answer = "Yes!! 11 meters per second"
    elif speed == 24:
        answer = "Yes!! 24 miles per hour"
    return {"answer": answer}
