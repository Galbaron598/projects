from data import ROOMS, LABELS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rooms")
def get_conference_rooms():
    return ROOMS

@app.get("/api/labels")
def get_labels():
    return LABELS

def get_capacity_by_label(label_id):
    output = 0
    for room in ROOMS:
        if label_id in room["labels"]:
            output += room["capacity"]
    return output
    

@app.get("/api/capacity")
def get_capacity():
    output = []
    for label in LABELS:
        toAppand ={"label":label["name"],"capacity":get_capacity_by_label(label["id"])  }
        # output[label["name"]] = get_capacity_by_label(label["id"])
        output.append(toAppand)
    return output

        
        
        
        
        
    




