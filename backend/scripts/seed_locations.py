# backend/scripts/seed_locations.py

import requests

BASE_URL = "http://127.0.0.1:8081"

USERNAME = "string"
PASSWORD = "string"


def login():
    form_data = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    res = requests.post(
        f"{BASE_URL}/users/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    res.raise_for_status()

    token = res.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def generate_locations():
    locations = []

    zones = ["A", "B", "C", "D"]

    for zone in zones:
        for rack in range(1, 6):
            for slot in range(1, 11):
                locations.append({
                    "location_name": f"{zone}-{rack:02d}-{slot:02d}",
                    "zone":zone
                })

    return locations


def seed_locations():
    headers = login()
    locations = generate_locations()

    success = 0
    failed = 0

    for location in locations:
        res = requests.post(
            f"{BASE_URL}/locations",
            json=location,
            headers=headers,
        )

        if res.status_code in [200, 201]:
            success += 1
        else:
            failed += 1
            print("실패:", location, res.status_code, res.text)

    print("로케이션 생성 완료")
    print("성공:", success)
    print("실패:", failed)


if __name__ == "__main__":
    seed_locations()