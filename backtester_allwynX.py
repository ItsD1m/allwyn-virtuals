import time
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

master_csv = "master_virtuals_matches.csv"

print("Συλλογή δεδομένων από τη σελίδα...")
driver = webdriver.Chrome()
driver.get("https://virtualsports.allwyn.gr/el/virtual-results")
time.sleep(15) 
page_text = driver.find_element(By.TAG_NAME, "body").text
driver.quit()

pattern = r'(\d+)-(\d+)\s*\n[^\n]+\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)\s*\n\|\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)'
matches = re.findall(pattern, page_text)

# Δημιουργία DataFrame με τα σημερινά ματς και χρονοσφραγίδα
today_matches = []
fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M")
for m in matches:
    today_matches.append({
        'timestamp': fetch_time,
        'home_goals': int(m[0]),
        'away_goals': int(m[1]),
        'odd_1': float(m[2]),
        'odd_x': float(m[3]),
        'odd_2': float(m[4]),
        'odd_u': float(m[5]),
        'odd_o': float(m[6])
    })

df_today = pd.DataFrame(today_matches)

# --- ΕΝΣΩΜΑΤΩΣΗ ΣΤΟ MASTER CSV ---
if os.path.exists(master_csv):
    master_df = pd.read_csv(master_csv)
    # Ενώνουμε και αφαιρούμε τυχόν διπλότυπα
    combined_df = pd.concat([master_df, df_today]).drop_duplicates(subset=['timestamp', 'home_goals', 'away_goals', 'odd_x'])
    combined_df.to_csv(master_csv, index=False)
    print(f"✅ Προστέθηκαν νέα δεδομένα. Συνολικά ματς στη βάση: {len(combined_df)}")
else:
    df_today.to_csv(master_csv, index=False)
    combined_df = df_today
    print(f"✅ Δημιουργήθηκε το master CSV με {len(combined_df)} αγώνες!")

# Ταξινόμηση σε απόλυτη χρονολογική σειρά
combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)

# --- ΣΥΝΕΧΕΣ BACKTEST ΣΕ ΟΛΟΚΛΗΡΗ ΤΗ ΒΑΣΗ ---
bankroll = 1000.0
starting_bankroll = bankroll
target_profit = 1.00
cumulative_loss = 0.0
max_bet_placed = 0.0

backtest_data = []

for i, row in combined_df.iterrows():
    home = int(row['home_goals'])
    away = int(row['away_goals'])
    odd_x = float(row['odd_x'])
    
    bet = (cumulative_loss + target_profit) / (odd_x - 1)
    bet = round(bet, 2)
    
    if bankroll < bet:
        print(f"💥 ΧΡΕΟΚΟΠΙΑ στο συνολικό ματς {i+1}!")
        break
        
    bankroll -= bet
    cumulative_loss += bet
    
    if bet > max_bet_placed:
        max_bet_placed = bet
        
    is_x = (home == away)
    
    if is_x:
        gross_return = bet * odd_x
        net_profit = gross_return - cumulative_loss
        bankroll += gross_return
        backtest_data.append({
            "Index": i+1,
            "Απόδοση": odd_x,
            "Ποντάρισμα": bet,
            "Αποτέλεσμα": "✅ WIN",
            "Κάβα": round(bankroll, 2)
        })
        cumulative_loss = 0.0
    else:
        backtest_data.append({
            "Index": i+1,
            "Απόδοση": odd_x,
            "Ποντάρισμα": bet,
            "Αποτέλεσμα": "❌ LOSS",
            "Κάβα": round(bankroll, 2)
        })

df_results = pd.DataFrame(backtest_data)

# --- ΕΜΦΑΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ---
print("=" * 75)
print(f" 📈 MULTI-DAY DYNAMIC RECOVERY BACKTEST ({len(df_results)} συνολικά ματς) ")
print("=" * 75)
print(f"Αρχική Κάβα: {starting_bankroll}€ | Τελική Κάβα: {round(bankroll, 2)}€")
print(f"Μέγιστο Ποντάρισμα (Max Drawdown): {max_bet_placed}€")
print("=" * 75)

# --- ΟΠΤΙΚΟΠΟΙΗΣΗ (EQUITY CURVE ΓΙΑ ΟΛΕΣ ΤΙΣ ΜΕΡΕΣ) ---
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
fig.suptitle(f'Multi-Day Backtest Equity Curve ({len(df_results)} Συνολικοί Αγώνες)', fontsize=16, fontweight='bold')

ax1.plot(df_results['Index'], df_results['Κάβα'], color='#00ff00', linewidth=1.5, label='Κάβα (€)')
ax1.set_ylabel('Κεφάλαιο (€)', fontsize=12)
ax1.grid(True, alpha=0.2, linestyle='--')
ax1.legend(loc='upper left')

rolling_max = df_results['Κάβα'].cummax()
drawdown = df_results['Κάβα'] - rolling_max

ax2.fill_between(df_results['Index'], drawdown, 0, color='#ff3333', alpha=0.6)
ax2.plot(df_results['Index'], drawdown, color='#ff0000', linewidth=1)
ax2.set_xlabel('Συνολικοί Αγώνες σε Βάθος Χρόνου', fontsize=12)
ax2.set_ylabel('Drawdown (€)', fontsize=12)
ax2.grid(True, alpha=0.2, linestyle='--')

plt.tight_layout()
plt.show()