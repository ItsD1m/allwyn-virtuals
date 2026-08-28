import time
import re
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

csv_filename = "virtuals_history_with_odds.csv"

print("Ανοίγει ο browser...")
driver = webdriver.Chrome()
driver.get("https://virtualsports.allwyn.gr/el/virtual-results")

print("Περιμένουμε 15 δευτερόλεπτα να φορτώσουν τα αποτελέσματα...")
time.sleep(15) 

page_text = driver.find_element(By.TAG_NAME, "body").text
driver.quit()

print("Αναλύονται τα δεδομένα...\n")

pattern = r'(\d+)-(\d+)\s*\n[^\n]+\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)\s*\n\|\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)'
matches = re.findall(pattern, page_text)

# ΑΝΤΙΣΤΡΟΦΗ για χρονολογική σειρά
matches.reverse()

valid_matches = []
# Προσθέσαμε το 'O' (Over) και 'U' (Under) στους μετρητές
delays = {'1': [], 'X': [], '2': [], 'O': [], 'U': []}
current_delay = {'1': 0, 'X': 0, '2': 0, 'O': 0, 'U': 0}

for m in matches:
    home = int(m[0])
    away = int(m[1])
    total_goals = home + away
    
    valid_matches.append({
        'home_goals': home,
        'away_goals': away,
        'odd_1': float(m[2]),
        'odd_x': float(m[3]),
        'odd_2': float(m[4]),
        'odd_u': float(m[5]),
        'odd_o': float(m[6])
    })
    
    # Λογική Καθυστερήσεων 1-X-2
    if home > away:
        delays['1'].append(current_delay['1'])
        current_delay['1'] = 0
        current_delay['X'] += 1
        current_delay['2'] += 1
    elif home == away:
        delays['X'].append(current_delay['X'])
        current_delay['X'] = 0
        current_delay['1'] += 1
        current_delay['2'] += 1
    else:
        delays['2'].append(current_delay['2'])
        current_delay['2'] = 0
        current_delay['1'] += 1
        current_delay['X'] += 1
        
    # Λογική Καθυστερήσεων Over/Under 2.5
    if total_goals >= 3:
        delays['O'].append(current_delay['O'])
        current_delay['O'] = 0
        current_delay['U'] += 1
    else:
        delays['U'].append(current_delay['U'])
        current_delay['U'] = 0
        current_delay['O'] += 1

df = pd.DataFrame(valid_matches)

if df.empty:
    print("ΣΦΑΛΜΑ: Δεν βρέθηκαν δεδομένα. Κάτι κόλλησε στη σελίδα του ΟΠΑΠ.")
else:
    total_matches = len(df)
    
    df['is_1'] = df['home_goals'] > df['away_goals']
    df['is_x'] = df['home_goals'] == df['away_goals']
    df['is_2'] = df['home_goals'] < df['away_goals']
    df['total_goals'] = df['home_goals'] + df['away_goals']
    df['is_over'] = df['total_goals'] >= 3
    
    pct_1, pct_x, pct_2 = df['is_1'].mean() * 100, df['is_x'].mean() * 100, df['is_2'].mean() * 100
    pct_over, pct_under = df['is_over'].mean() * 100, (1 - df['is_over'].mean()) * 100
    avg_odd_1, avg_odd_x, avg_odd_2 = df['odd_1'].mean(), df['odd_x'].mean(), df['odd_2'].mean()
    avg_odd_over, avg_odd_under = df['odd_o'].mean(), df['odd_u'].mean()
    
    # Μέγιστες Καθυστερήσεις Ημέρας
    max_1 = max(delays['1']) if delays['1'] else 0
    max_x = max(delays['X']) if delays['X'] else 0
    max_2 = max(delays['2']) if delays['2'] else 0
    max_o = max(delays['O']) if delays['O'] else 0
    max_u = max(delays['U']) if delays['U'] else 0

    # --- ΕΚΤΥΠΩΣΗ ---
    print("=" * 95)
    print(f" 📊 ΒΡΕΘΗΚΑΝ {total_matches} ΑΓΩΝΕΣ")
    print("=" * 95)
    print(f"Άσσος (1) : {pct_1:.1f}% \t| Μέση Απόδ: {avg_odd_1:.2f} \t| ⏳ Αγνοείται: {current_delay['1']:>2} αγώνες (Max ημέρας: {max_1})")
    print(f"Χι (X)    : {pct_x:.1f}% \t| Μέση Απόδ: {avg_odd_x:.2f} \t| ⏳ Αγνοείται: {current_delay['X']:>2} αγώνες (Max ημέρας: {max_x})")
    print(f"Διπλό (2) : {pct_2:.1f}% \t| Μέση Απόδ: {avg_odd_2:.2f} \t| ⏳ Αγνοείται: {current_delay['2']:>2} αγώνες (Max ημέρας: {max_2})")
    print("-" * 95)
    print(f"Over 2.5  : {pct_over:.1f}% \t| Μέση Απόδ: {avg_odd_over:.2f} \t| ⏳ Αγνοείται: {current_delay['O']:>2} αγώνες (Max ημέρας: {max_o})")
    print(f"Under 2.5 : {pct_under:.1f}% \t| Μέση Απόδ: {avg_odd_under:.2f} \t| ⏳ Αγνοείται: {current_delay['U']:>2} αγώνες (Max ημέρας: {max_u})")
    print("=" * 95)

    # --- ΑΠΟΘΗΚΕΥΣΗ ΣΤΗ ΜΝΗΜΗ (CSV) ΚΑΙ ΣΥΓΚΡΙΣΗ ---
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data = pd.DataFrame([{
        "Date": today_date,
        "Total_Matches": total_matches,
        "1_pct": pct_1, "X_pct": pct_x, "2_pct": pct_2,
        "Over_pct": pct_over, "Under_pct": pct_under,
        "Avg_Odd_1": avg_odd_1, "Avg_Odd_X": avg_odd_x, "Avg_Odd_2": avg_odd_2,
        "Avg_Odd_Over": avg_odd_over, "Avg_Odd_Under": avg_odd_under
    }])

    if os.path.exists(csv_filename):
        history_df = pd.read_csv(csv_filename)
        hist_1 = history_df['1_pct'].mean()
        hist_over = history_df['Over_pct'].mean()
        
        print("\n🤖 [ ΣΥΓΚΡΙΣΗ ΜΕ ΤΟ ΠΑΡΕΛΘΟΝ ]")
        print(f"Ιστορικό Over 2.5: {hist_over:.1f}%  --> Σήμερα: {pct_over:.1f}%")
        
        if abs(pct_over - hist_over) > 10:
            print(f"⚠️ ALERT: Μεγάλη απόκλιση στο Over 2.5 (Διαφορά {pct_over - hist_over:.1f}%)")

        updated_df = pd.concat([history_df, new_data], ignore_index=True)
        updated_df.to_csv(csv_filename, index=False)
        print("\n✅ Τα δεδομένα αποθηκεύτηκαν στο CSV!")
    else:
        new_data.to_csv(csv_filename, index=False)
        print("\n✅ Δημιουργήθηκε η βάση δεδομένων (CSV) για πρώτη φορά!")