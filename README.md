# 🌐 OSINT Engine - Advanced Web Scraper

OSINT Engine is an **Open-Source Intelligence (OSINT) Scraper** designed to automatically search data on search engines (**Google, Bing, DuckDuckGo**) using **Selenium WebDriver**.

⚠️ **IMPORTANT NOTICE:**  
- **This script cannot be run in a CLI-only (headless) environment**  
- **Requires a GUI (Graphical User Interface) to trigger Chrome WebDriver**  
- **Must be run on a system with a desktop environment (Linux, Windows, macOS)**  

---

## ✨ **Features**
✔ Scrapes from **Google, Bing, and DuckDuckGo**  
✔ Filters results for **specific platforms (Twitter, Facebook, GitHub, etc.)**  
✔ **Cleans output** by removing unnecessary Google redirects  
✔ Saves results in **TXT, CSV, or JSON** formats  
✔ **Displays a progress bar** to show scraping status  

---

## ⚙️ **Requirements**
OSINT Engine requires the following dependencies:

### **1️⃣ Supported Operating Systems**
✅ **Linux** (Ubuntu, Debian, Kali, Arch)  
✅ **Windows** (WSL2 + GUI or Native)  
✅ **macOS**  

---

### **2️⃣ Required Packages**
- **Python 3.x**
- **Google Chrome Stable**
- **ChromeDriver (via WebDriver Manager)**
- **Selenium & BeautifulSoup**

---

## 📌 **Installation Guide (Linux/macOS)**
Run the following commands in the terminal:

```bash
# 1️⃣ Update system & install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip unzip wget curl

# 2️⃣ Install Google Chrome Stable
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y

# 3️⃣ Install Python dependencies
pip3 install -r requirements.txt
```

📌 **For Arch Linux users:**  
```bash
sudo pacman -S google-chrome python-pip
pip3 install -r requirements.txt
```

---

## 📌 **Installation Guide (Windows)**
1. **Install Python 3.x** from [Python Official Website](https://www.python.org/downloads/)  
2. **Install Google Chrome** from [Google Chrome Download](https://www.google.com/chrome/)  
3. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

---

## 🔌 **How to Run OSINT Engine**
⚠️ **Ensure you are running this on a GUI/Desktop environment, as Selenium requires a visible Chrome instance!**

### **1️⃣ Run Scraping without Platform Filter**
```bash
python3 osint_main.py "domain.com slot gacor" --engine google --pages 3 --output txt --filename results
```
📌 **Results will be saved as:** `results.txt`

---

### **2️⃣ Scraping with Twitter Filter**
```bash
python3 osint_main.py "leaked credentials" --platform twitter --engine google --pages 3 --output txt --filename twitter_results
```
📌 **Only searches on Twitter (`site:twitter.com OR site:x.com`)**

---

### **3️⃣ Scraping with Google Drive Filter**
```bash
python3 osint_main.py "confidential file" --platform gdrive --engine google --pages 3 --output csv --filename gdrive_files
```
📌 **Only searches on Google Drive (`site:drive.google.com`)**

---

### **4️⃣ Scraping on Bing & DuckDuckGo**
```bash
# Search on Bing
python3 osint_main.py "site:pastebin.com leaks" --engine bing --pages 5 --output csv --filename bing_results

# Search on DuckDuckGo
python3 osint_main.py "hacked sites list" --engine duckduckgo --pages 3 --output json --filename duckduckgo_results
```

---

## 📁 **Supported Output Formats**
| Format | Command |
|--------|---------|
| `.txt` | `--output txt --filename results` |
| `.csv` | `--output csv --filename results` |
| `.json` | `--output json --filename results` |

To view results:
```bash
cat results.txt   # For TXT
cat results.csv   # For CSV
cat results.json  # For JSON
```

---

## ⚠️ **Troubleshooting**
### **1️⃣ Error: `Session not created: Chrome failed to start`**
✔ **Solution:**  
- Ensure Google Chrome is installed and can be opened manually  
- Try running:
```bash
google-chrome --version
```
- If the error persists, reinstall Chrome:
```bash
sudo apt purge google-chrome-stable
sudo apt install -y google-chrome-stable
```

---

### **2️⃣ Error: `Selenium WebDriver Error: Cannot find Chrome binary`**
✔ **Solution:**  
- Make sure Chrome is in the system `PATH`  
- Check Chrome location:
```bash
which google-chrome
```
- If not found, add Chrome to `PATH`:
```bash
export PATH=$PATH:/usr/bin/google-chrome-stable
```

---

## 📝 **Important Notes**
- **This script requires a GUI (not CLI-only/server headless mode)**  
- **If using a headless server/VPS, use VNC or RDP to run the script**  
- **If you still want headless mode, modify Selenium options to `--headless` (not recommended)**  

---

## 🎯 **Conclusion**
✔ **Automated OSINT Scraper for Google, Bing, DuckDuckGo**  
✔ **Supports targeted searches (Twitter, Facebook, GitHub, etc.)**  
✔ **Filters out unwanted Google redirects & irrelevant links**  
✔ **Supports output in `.txt`, `.csv`, and `.json` formats**  
✔ **Requires a GUI to run Selenium Chrome Driver**  

🚀 **Use responsibly! Do not engage in illegal activities!** 🚀


## **📌 How to Use this README.md on GitHub**
After creating your repository on GitHub, follow these steps:

### **1️⃣ Clone Repository Locally**
```bash
git clone https://github.com/threatlabindonesia/INTELL-OSINT-AND-CONTENT-CHECKER.git
cd INTELL-OSINT-AND-CONTENT-CHECKER
```
