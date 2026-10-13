"""Hospital Resource & Patient Management System
Module 1 (Utility 1): Patient Record Management
Author: Aryan Ashok Patre | USN: CD25071 | CSE-DS (B)
"""
import json, os
from datetime import datetime

FILE = "patients.json"

def load():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return json.load(f)
    return {}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def new_id(data):
    return "P" + str(len(data) + 1).zfill(3)          # P001, P002 ...

def register(data, name, age, gender, phone, disease):
    if not name.strip() or not (0 < age < 120) or not phone.isdigit() or len(phone) != 10:
        return None                                    # validation failed
    pid = new_id(data)
    data[pid] = {"name": name, "age": age, "gender": gender, "phone": phone,
                 "admitted_on": datetime.now().strftime("%d-%m-%Y"),
                 "history": [{"date": datetime.now().strftime("%d-%m-%Y"), "note": disease}]}
    save(data)
    return pid

def search(data, key):
    key = key.lower()
    return {p: r for p, r in data.items() if key == p.lower() or key in r["name"].lower()}

def update(data, pid, field, value):
    if pid in data and field in ("name", "age", "phone", "gender"):
        data[pid][field] = value
        save(data)
        return True
    return False

def add_history(data, pid, note):
    if pid in data:
        data[pid]["history"].append({"date": datetime.now().strftime("%d-%m-%Y"), "note": note})
        save(data)
        return True
    return False

def delete(data, pid):
    if data.pop(pid, None) is not None:
        save(data)
        return True
    return False

def show(pid, r):
    print(f"{pid} | {r['name']} | {r['age']} | {r['gender']} | {r['phone']}")
    for h in r["history"]:
        print(f"    - {h['date']}: {h['note']}")

def menu():
    data = load()
    while True:
        print("\n=== PATIENT RECORD MANAGEMENT ===")
        print("1.Register  2.Search  3.Update  4.Add Treatment Note  5.View All  6.Delete  7.Exit")
        ch = input("Choice: ").strip()
        if ch == "1":
            pid = register(data, input("Name: "), int(input("Age: ")), input("Gender: "),
                           input("Phone (10 digits): "), input("Problem/Disease: "))
            print("Registered! ID =", pid) if pid else print("Invalid details!")
        elif ch == "2":
            res = search(data, input("Enter ID or name: "))
            [show(p, r) for p, r in res.items()] if res else print("Not found")
        elif ch == "3":
            print("Updated" if update(data, input("ID: "), input("Field: "), input("New value: ")) else "Failed")
        elif ch == "4":
            print("Added" if add_history(data, input("ID: "), input("Note: ")) else "ID not found")
        elif ch == "5":
            [show(p, r) for p, r in data.items()] or print("No records")
        elif ch == "6":
            print("Deleted" if delete(data, input("ID: ")) else "ID not found")
        elif ch == "7":
            print("Data saved. Bye!"); break

if __name__ == "__main__":
    menu()
