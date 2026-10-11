# create_sample_data.py
import pandas as pd
import random
import datetime

# --- SETTINGS ---
num_transactions = 100
categories = ['Groceries', 'Transport', 'Dining', 'Shopping', 'Wellness']
descriptions = {
    'Groceries': ['Safeway', 'Whole Foods', 'Trader Joes', 'City Market'],
    'Transport': ['Uber', 'Lyft', 'Gas Station', 'Subway'],
    'Dining': ['Starbucks', 'McDonalds', 'Dominos', 'Taco Bell', 'Panera'],
    'Shopping': ['Amazon', 'Target', 'Best Buy', 'H&M', 'Nike'],
    'Wellness': ['CVS Pharmacy', 'Gym', 'Yoga Class', 'Massage']
}
start_date = datetime.date(2025, 1, 1)

# --- GENERATE DATA ---
data = []
for i in range(num_transactions):
    # Random category and description
    category = random.choice(categories)
    description = random.choice(descriptions[category])
    
    # Amount between 5 and 150
    amount = round(random.uniform(5, 150), 2)
    
    # Generate a random date in 2025
    date = start_date + datetime.timedelta(days=random.randint(0, 300))
    
    data.append([date, description, amount, category])

# --- CREATE DATAFRAME AND SAVE ---
df = pd.DataFrame(data, columns=['date', 'description', 'amount', 'category'])
df.to_csv('expenses.csv', index=False)

print("expenses.csv file created successfully with sample data!")