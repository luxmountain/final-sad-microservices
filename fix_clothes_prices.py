import requests

CLOTHES_URL = "http://localhost:8013/clothes/"

def fix_prices():
    try:
        response = requests.get(CLOTHES_URL)
        if response.status_code != 200:
            print(f"Failed to fetch clothes: {response.status_code}")
            return
            
        clothes = response.json()
        count = 0
        for c in clothes:
            current_price = float(c["price"])
            # If price is unusually small (e.g. < 100,000), it's probably USD
            if current_price < 100000:
                new_price = current_price * 25000.0
                c["price"] = new_price
                
                update_url = f"{CLOTHES_URL}{c['id']}/"
                res = requests.put(update_url, json=c)
                if res.status_code in (200, 201):
                    count += 1
                else:
                    print(f"Failed to update item {c['id']}: {res.text}")
                    
        print(f"Successfully updated {count} clothes items to VND.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_prices()
