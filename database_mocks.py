import requests

data = [
    {
        "owner": "Alice Smith",
        "balance": 40000
        
    },

    {
        "owner": "Bob Johnson",
        "balance": 432000
    },
    {
        "owner": "Chidi Okeke",
        "balance": 129000
    },

    
  {
    "owner": "Tunde Bakare",
    "balance": 330000
    
  },
  {
    "owner": "Fatima Umar",
    "balance": 550000
    
  },

  {
    "owner": "Mark Adetunde",
    "balance": 679000
  },
  {
    "owner": "Sola Adebayo",
    "balance": 78000
  },
  {
    "owner": "Grace Danjuma",
    "balance": 320000
  },
  {
    "owner": "Kelechi Okafor",
    "balance": 110000
  },
  {
    "owner": "Amina Bello",
    "balance": 990000
  },
  {
    "owner": "David Oladipo",
    "balance": 3392000
  },
  {
    "owner": "Blessing Eze",
    "balance":190000
  },
  {
    "owner": "Yusuf Hassan",
    "balance": 500000
  }

]


url = "http://127.0.0.1:8000/accounts"

for stop in data:
    response = requests.post(url, json=stop)
    print(response.status_code, response.json())