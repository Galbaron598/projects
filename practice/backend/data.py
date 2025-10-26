ROOMS = [
    {"id": 1, "name": "Room A", "buildingName": "HQ", "labels": [1], "capacity": 30, "hasProjector": True},
    {"id": 2, "name": "Room B", "buildingName": "HQ", "labels": [2, 3], "capacity": 10, "hasProjector": False},
    {"id": 3, "name": "Room C", "buildingName": "Remote", "labels": [4], "capacity": 20, "hasTv": True},
]

LABELS = [
    {"id": 1, "name": "Large", "parentId": None},
    {"id": 2, "name": "Small", "parentId": None},
    {"id": 3, "name": "Remote", "parentId": None},
    {"id": 4, "name": "Sub Remote", "parentId": 3},
]
