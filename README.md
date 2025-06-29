# PyBuildingEnergy - Διπλωματική Εργασία

Αυτό το αποθετήριο περιέχει προσομοιώσεις ενεργειακής κατανάλωσης κτηρίων χρησιμοποιώντας το εργαλείο **PyBuildingEnergy**.

## 🔧 Δομή του Αποθετηρίου

### 📁 `Ignatis`
Αρχικός φάκελος του project.

### 📁 `Actual_Building`
Περιέχει **4 αρχεία Python**, καθένα από τα οποία προσομοιώνει ένα διαφορετικό πραγματικό κτήριο.  
Τα αποτελέσματα αποθηκεύονται σε ξεχωριστούς υποφακέλους:
- `Result`, `Result2`, `Result3`, `Result4`

Αρχεία Python:
- `actual_building.py`
- `actual_building2.py`
- `actual_building3.py`
- `actual_building4.py`

#### Τα τελικά input δεδομένα για κάθε πραγματικό κτήριο είναι:
- Πόσοι μένουν στο σπίτι  
- Πόσα υπνοδωμάτια έχει  
- Πότε χτίστηκε  
- Αν έγινε ριζική ανακαίνιση (και πότε)  
- Κλιματική ζώνη  
- Τύπος Τοίχων  
- Τύπος Τελικής Επιφάνειας  
- Τύπος Στέγης  
- Τύπος Δαπέδου  
- Τύπος Παραθύρων  
- Τύπος λέβητα  
- Τύπος καυσίμου  

### 📁 `Reference_Building`
Προσομοίωση του **κτηρίου αναφοράς** με βάση τις προδιαγραφές του ΚΕΝΑΚ.  
Η εκτέλεση του αρχείου δημιουργεί τα αποτελέσματα στον δικό του φάκελο `results`.

### 📁 `weather`
Περιέχει το αρχείο καιρού:
- `GRC_Athens_modified_for_kenak.epw`

Αυτό χρησιμοποιείται σε όλες τις προσομοιώσεις για σωστή αντιστοίχιση με την Κλιματική Ζώνη Α (Αθήνα).

### 📁 `ActualSimulation`
Απόπειρα για μια πιο ευέλικτη εκδοχή της προσομοίωσης πραγματικού κτηρίου με **δυναμικά inputs από τον χρήστη**.  
⚠️ *Αυτή η υλοποίηση δεν είναι πλήρως λειτουργική προς το παρόν.*

---

## ▶️ Πώς να τρέξετε τις προσομοιώσεις

1. Εγκαταστήστε το πακέτο `pybuildingenergy`.
2. Εκτελέστε το αρχείο:
   - Για reference: από τον φάκελο `Reference_Building`
   - Για πραγματικά κτήρια: τα `actual_buildingX.py` από τον φάκελο `Actual_Building`
3. Τα αποτελέσματα δημιουργούνται αυτόματα στους αντίστοιχους φακέλους (`results`, `Result2`, κ.λπ.)
