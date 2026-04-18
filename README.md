# Tamper-Evident Logging System

A secure logging system that ensures the **integrity and reliability of logs** by preventing undetected modification, deletion, or reordering of log entries.

This project uses a **hash-chaining mechanism (similar to blockchain)** where each log is cryptographically linked to the previous one. Any change in past logs breaks the chain and is immediately detected.

---

##  Features

-  Hash-based log chaining (SHA-256)
-  Tamper detection (modification, deletion, reordering)
-  Secure log entry system
-  Admin dashboard to view logs
-  Fake login (deception system) to capture suspicious activity
-  Log integrity verification

---

##  How It Works

Each log entry contains:

- Timestamp  
- Event type  
- Description  
- Previous hash  
- Current hash  

###  Process:
1. First log (GENESIS) is created  
2. Each new log stores the hash of the previous log  
3. A new hash is generated using log data + previous hash  
4. During verification:
   - If any log is changed → hash mismatch  
   - System detects tampering instantly  



