# BankEase — Banking Management System
**Stack:** Python, Tkinter, Oracle Database Free, PL/SQL, python-oracledb  
**Type:** Academic MCA mini-project

## Features
- Customer creation and directory
- Savings/current account opening
- Deposit, withdrawal and account-to-account transfer
- Account balances, dashboard totals, transaction history
- Oracle PL/SQL procedures validate and perform money operations

> Oracle SQL Developer or the VS Code Oracle extension is only a client. A running Oracle Database is required. This project does not use SQLite.

## 1. Prerequisites
1. Install Oracle Database Free for Windows (or use a running Oracle instance).
2. Install Python 3.10+ and VS Code.
3. Open this folder in VS Code, then in its terminal run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Optionally install the VS Code Oracle extension, or use Oracle SQL Developer to run the SQL scripts.

## 2. Create the schema
Connect as `SYSTEM` to the correct Oracle pluggable database/service. For Oracle Database Free, `FREEPDB1` is commonly the PDB service; some installations expose other service names. Verify the actual service configured on your machine.

Run `sql/00_create_user.sql` as an administrator. Then connect as:
- User: `bank_user`
- Password: `ChangeMe_Bank_123`
- Host: `localhost`
- Port: `1521`
- Service: `FREEPDB1` (or your verified service name)

Change the sample password for any use beyond a local classroom demo.

## 3. Run database scripts
While connected as `bank_user`, execute these scripts in order:
1. `sql/01_schema.sql`
2. `sql/02_plsql_programs.sql`
3. `sql/03_sample_data.sql` (optional demo records; run only once)
4. `sql/04_verify.sql`

In SQL Developer, use **Run Script (F5)**. In VS Code, use the Oracle extension's **Run Script** action. Check for compilation errors if any object is invalid.

## 4. Configure Python
Edit `app/db_config.py` to match the database host, port, service name, username and password.

`python-oracledb` uses Thin mode by default; a separate Oracle Client installation is usually not required for a normal TCP connection.

## 5. Launch
From the project root:
```powershell
.\.venv\Scripts\Activate.ps1
python app\main.py
```
If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or launch directly with `.venv\Scripts\python.exe app\main.py`.

## 6. Demo sequence
1. Add a customer and note the Customer ID.
2. Open an account with an initial deposit.
3. Deposit money, then withdraw less than the balance.
4. Open a second account and transfer money between the two.
5. Refresh Accounts and Transactions tabs to show updated balances/history.
6. Explain `p_deposit`, `p_withdraw`, and `p_transfer` in `sql/02_plsql_programs.sql`.

## Troubleshooting
- **ORA-12514 / service unknown:** verify service name; try the actual PDB service (often `FREEPDB1`) rather than assuming `FREE`.
- **ORA-01017:** credentials do not match; reset the schema password and update `app/db_config.py`.
- **ORA-01031:** run the user script as an administrator or grant required privileges.
- **PL/SQL invalid:** inspect `USER_ERRORS` or run `SHOW ERRORS`.
- **Connection refused / DPY-6001:** start the Oracle Database/listener service and verify host/port.
- **ModuleNotFoundError: oracledb:** activate the virtual environment and run `pip install -r requirements.txt`.

## Academic scope
This is a classroom prototype, not production banking software. It does not implement production authentication, role-based authorization, fraud controls, encryption/key management, or regulatory compliance. Use fictional demo data only.
