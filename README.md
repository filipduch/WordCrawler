# WordCrawler - Test Application

## Installation
1) Clone the repository
2) Create python virtualenv
3) Run pip install --no-cache-dir -r requirements.txt
4) Edit Config.py (db_* fields)
5) Run python3 WebServer.py
6) *It is recommended to use above steps instead of Docker because some error appears*

## Safely keeping encryption keys
- Use an external Hardware Security Module
- Protect decryption key with passphrase
- Type the decryption passphrase on system start-up and store it in the RAM
- Store the decryption key on a different server
