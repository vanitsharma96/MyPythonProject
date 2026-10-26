import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation
from contextlib import closing
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_connection, query_all, call_procedure

BG, INK = "#f3f6fb", "#172033"

class BankEaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BankEase | Banking Management System")
        self.geometry("1120x720"); self.minsize(950, 620); self.configure(bg=BG)
        self.style()
        top = tk.Frame(self, bg=INK, height=78); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text="BankEase", bg=INK, fg="white", font=("Segoe UI", 22, "bold")).pack(side="left", padx=24, pady=16)
        tk.Label(top, text="BANKING MANAGEMENT SYSTEM  •  PYTHON + ORACLE PL/SQL", bg=INK, fg="#c9d4ed", font=("Segoe UI", 10)).pack(side="left", padx=12)
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill="both", expand=True, padx=18, pady=18)
        self.build_dashboard(); self.build_customers(); self.build_accounts(); self.build_operations(); self.build_transactions()
        self.refresh_all()

    def style(self):
        s=ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("TFrame",background=BG); s.configure("TLabel",background=BG,foreground=INK,font=("Segoe UI",10))
        s.configure("Title.TLabel",font=("Segoe UI",20,"bold"),foreground=INK)
        s.configure("TButton",font=("Segoe UI",10),padding=7)
        s.configure("Treeview",rowheight=27,font=("Segoe UI",9))
        s.configure("Treeview.Heading",font=("Segoe UI",9,"bold"))
        s.configure("TNotebook.Tab",padding=(14,8),font=("Segoe UI",10,"bold"))

    def tab(self,title):
        f=ttk.Frame(self.tabs,padding=16); self.tabs.add(f,text=title); return f

    def entry(self,parent,label,row,col,width=28):
        ttk.Label(parent,text=label).grid(row=row,column=col,sticky="w",padx=6,pady=5)
        e=ttk.Entry(parent,width=width); e.grid(row=row+1,column=col,sticky="ew",padx=6,pady=(0,10)); return e

    def tree(self,parent,cols,heads,height=14):
        w=ttk.Frame(parent); w.pack(fill="both",expand=True,pady=10)
        t=ttk.Treeview(w,columns=cols,show="headings",height=height)
        ys=ttk.Scrollbar(w,orient="vertical",command=t.yview); xs=ttk.Scrollbar(w,orient="horizontal",command=t.xview)
        t.configure(yscrollcommand=ys.set,xscrollcommand=xs.set)
        t.grid(row=0,column=0,sticky="nsew"); ys.grid(row=0,column=1,sticky="ns"); xs.grid(row=1,column=0,sticky="ew")
        w.rowconfigure(0,weight=1); w.columnconfigure(0,weight=1)
        for c,h in zip(cols,heads): t.heading(c,text=h); t.column(c,width=130,anchor="w")
        return t

    def build_dashboard(self):
        f=self.tab("Dashboard"); ttk.Label(f,text="Overview",style="Title.TLabel").pack(anchor="w",pady=(0,14))
        cards=ttk.Frame(f); cards.pack(fill="x"); self.card_vars={}
        for key,title in [("customers","Customers"),("accounts","Accounts"),("balance","Active Balance (₹)"),("transactions","Transactions")]:
            box=tk.Frame(cards,bg="white",highlightbackground="#dce3ef",highlightthickness=1)
            box.pack(side="left",fill="both",expand=True,padx=6,pady=6)
            tk.Label(box,text=title,bg="white",fg="#5a6680",font=("Segoe UI",10)).pack(anchor="w",padx=15,pady=(14,4))
            v=tk.StringVar(value="—"); self.card_vars[key]=v
            tk.Label(box,textvariable=v,bg="white",fg=INK,font=("Segoe UI",20,"bold")).pack(anchor="w",padx=15,pady=(0,14))
        ttk.Label(f,text="Recent activity",style="Title.TLabel").pack(anchor="w",pady=(22,0))
        self.recent_tree=self.tree(f,("id","type","amount","from","to","date"),("Txn ID","Type","Amount (₹)","From","To","Created"),10)

    def build_customers(self):
        f=self.tab("Customers"); ttk.Label(f,text="Customer Management",style="Title.TLabel").pack(anchor="w",pady=(0,12))
        form=ttk.Frame(f); form.pack(fill="x")
        self.c_name=self.entry(form,"Full name *",0,0); self.c_email=self.entry(form,"Email",0,1)
        self.c_phone=self.entry(form,"Phone",0,2); self.c_address=self.entry(form,"Address",2,0,60)
        ttk.Button(form,text="Add Customer",command=self.add_customer).grid(row=3,column=0,padx=6,pady=4,sticky="w")
        ttk.Button(form,text="Refresh",command=self.refresh_customers).grid(row=3,column=1,padx=6,pady=4,sticky="w")
        self.customer_tree=self.tree(f,("id","name","email","phone","address","created"),("Customer ID","Full Name","Email","Phone","Address","Created"),12)

    def build_accounts(self):
        f=self.tab("Accounts"); ttk.Label(f,text="Account Directory",style="Title.TLabel").pack(anchor="w",pady=(0,12))
        ttk.Label(f,text="Create accounts in Operations. Refresh to view current balances.").pack(anchor="w")
        ttk.Button(f,text="Refresh Accounts",command=self.refresh_accounts).pack(anchor="w",pady=8)
        self.account_tree=self.tree(f,("id","customer","name","type","balance","status","opened"),("Account ID","Customer ID","Customer","Type","Balance (₹)","Status","Opened"),16)

    def build_operations(self):
        f=self.tab("Operations"); ttk.Label(f,text="Banking Operations",style="Title.TLabel").pack(anchor="w",pady=(0,12))
        ttk.Label(f,text="Deposit, withdrawal and transfer rules are enforced in Oracle PL/SQL.").pack(anchor="w",pady=(0,12))
        nb=ttk.Notebook(f); nb.pack(fill="both",expand=True)
        a=ttk.Frame(nb,padding=18); nb.add(a,text="Open Account")
        self.open_customer=self.entry(a,"Customer ID *",0,0)
        ttk.Label(a,text="Account type").grid(row=0,column=1,sticky="w",padx=6,pady=5)
        self.open_type=ttk.Combobox(a,values=["SAVINGS","CURRENT"],state="readonly",width=25); self.open_type.current(0)
        self.open_type.grid(row=1,column=1,sticky="w",padx=6,pady=(0,10))
        self.open_amount=self.entry(a,"Initial deposit (₹)",0,2)
        ttk.Button(a,text="Open Account",command=self.open_account).grid(row=2,column=0,padx=6,pady=10,sticky="w")
        ttk.Label(a,text="Use the Customer ID displayed in the Customers tab.").grid(row=3,column=0,columnspan=3,sticky="w",padx=6)
        b=ttk.Frame(nb,padding=18); nb.add(b,text="Deposit / Withdraw")
        self.money_account=self.entry(b,"Account ID *",0,0); self.money_amount=self.entry(b,"Amount (₹) *",0,1); self.money_note=self.entry(b,"Note",0,2)
        ttk.Button(b,text="Deposit",command=lambda:self.money_operation("deposit")).grid(row=2,column=0,padx=6,pady=10,sticky="w")
        ttk.Button(b,text="Withdraw",command=lambda:self.money_operation("withdraw")).grid(row=2,column=1,padx=6,pady=10,sticky="w")
        c=ttk.Frame(nb,padding=18); nb.add(c,text="Transfer")
        self.from_id=self.entry(c,"From Account ID *",0,0); self.to_id=self.entry(c,"To Account ID *",0,1)
        self.transfer_amount=self.entry(c,"Amount (₹) *",0,2); self.transfer_note=self.entry(c,"Note",2,0,40)
        ttk.Button(c,text="Transfer Money",command=self.transfer).grid(row=4,column=0,padx=6,pady=10,sticky="w")

    def build_transactions(self):
        f=self.tab("Transactions"); ttk.Label(f,text="Transaction History",style="Title.TLabel").pack(anchor="w",pady=(0,12))
        ttk.Button(f,text="Refresh History",command=self.refresh_transactions).pack(anchor="w")
        self.txn_tree=self.tree(f,("id","type","amount","from","to","note","date"),("Txn ID","Type","Amount (₹)","From","To","Note","Created"),16)

    def money(self,text,label,zero=False):
        try: n=Decimal(text.strip())
        except (InvalidOperation,AttributeError): raise ValueError(f"{label} must be a valid number.")
        if not n.is_finite() or n<0 or (n==0 and not zero): raise ValueError(f"{label} must be {'zero or greater' if zero else 'greater than zero'}.")
        if n.as_tuple().exponent < -2: raise ValueError(f"{label} can have at most two decimal places.")
        return n

    def integer(self,text,label):
        try: n=int(text.strip())
        except (ValueError,AttributeError): raise ValueError(f"{label} must be a whole number.")
        if n<=0: raise ValueError(f"{label} must be positive.")
        return n

    def action(self,fn):
        try: fn(); self.refresh_all()
        except Exception as e: messagebox.showerror("Operation failed",str(e))

    def add_customer(self):
        def run():
            name=self.c_name.get().strip()
            if not name: raise ValueError("Full name is required.")
            with closing(get_connection()) as conn:
                with conn.cursor() as cur:
                    out=cur.var(int)
                    cur.callproc("p_create_customer",[name,self.c_email.get().strip(),self.c_phone.get().strip(),self.c_address.get().strip(),out])
                    cid=out.getvalue()
            messagebox.showinfo("Success",f"Customer created. Customer ID: {cid}")
            for e in (self.c_name,self.c_email,self.c_phone,self.c_address): e.delete(0,"end")
        self.action(run)

    def open_account(self):
        def run():
            cid=self.integer(self.open_customer.get(),"Customer ID")
            amt=self.money(self.open_amount.get() or "0","Initial deposit",True)
            with closing(get_connection()) as conn:
                with conn.cursor() as cur:
                    out=cur.var(int); cur.callproc("p_open_account",[cid,self.open_type.get(),amt,out]); aid=out.getvalue()
            messagebox.showinfo("Success",f"Account opened. Account ID: {aid}")
            self.open_customer.delete(0,"end"); self.open_amount.delete(0,"end")
        self.action(run)

    def money_operation(self,kind):
        def run():
            aid=self.integer(self.money_account.get(),"Account ID"); amt=self.money(self.money_amount.get(),"Amount")
            proc="p_deposit" if kind=="deposit" else "p_withdraw"
            call_procedure(proc,[aid,amt,self.money_note.get().strip()])
            messagebox.showinfo("Success",f"{kind.title()} completed successfully.")
            self.money_amount.delete(0,"end"); self.money_note.delete(0,"end")
        self.action(run)

    def transfer(self):
        def run():
            src=self.integer(self.from_id.get(),"Source Account ID"); dst=self.integer(self.to_id.get(),"Destination Account ID")
            amt=self.money(self.transfer_amount.get(),"Amount")
            call_procedure("p_transfer",[src,dst,amt,self.transfer_note.get().strip()])
            messagebox.showinfo("Success","Transfer completed successfully.")
            for e in (self.from_id,self.to_id,self.transfer_amount,self.transfer_note): e.delete(0,"end")
        self.action(run)

    def fill(self,tree,rows):
        for i in tree.get_children(): tree.delete(i)
        for row in rows: tree.insert("","end",values=tuple("" if x is None else str(x) for x in row))

    def refresh_customers(self):
        self.fill(self.customer_tree,query_all("SELECT customer_id,full_name,email,phone,address,TO_CHAR(created_at,'YYYY-MM-DD HH24:MI') FROM customers ORDER BY customer_id DESC"))

    def refresh_accounts(self):
        self.fill(self.account_tree,query_all("SELECT account_id,customer_id,full_name,account_type,TO_CHAR(balance,'FM9999999990.00'),status,TO_CHAR(opened_at,'YYYY-MM-DD HH24:MI') FROM v_account_summary ORDER BY account_id DESC"))

    def refresh_transactions(self):
        self.fill(self.txn_tree,query_all("SELECT transaction_id,transaction_type,TO_CHAR(amount,'FM9999999990.00'),from_account_id,to_account_id,note,TO_CHAR(created_at,'YYYY-MM-DD HH24:MI') FROM v_transaction_history ORDER BY transaction_id DESC FETCH FIRST 250 ROWS ONLY"))

    def refresh_dashboard(self):
        r=query_all("SELECT (SELECT COUNT(*) FROM customers),(SELECT COUNT(*) FROM accounts),(SELECT NVL(SUM(balance),0) FROM accounts WHERE status='ACTIVE'),(SELECT COUNT(*) FROM transactions) FROM dual")[0]
        self.card_vars["customers"].set(str(r[0])); self.card_vars["accounts"].set(str(r[1]))
        self.card_vars["balance"].set(f"{r[2]:,.2f}"); self.card_vars["transactions"].set(str(r[3]))
        recent=query_all("SELECT transaction_id,transaction_type,TO_CHAR(amount,'FM9999999990.00'),from_account_id,to_account_id,TO_CHAR(created_at,'YYYY-MM-DD HH24:MI') FROM transactions ORDER BY transaction_id DESC FETCH FIRST 10 ROWS ONLY")
        self.fill(self.recent_tree,recent)

    def refresh_all(self):
        try:
            self.refresh_dashboard(); self.refresh_customers(); self.refresh_accounts(); self.refresh_transactions()
        except Exception as e:
            messagebox.showerror("Database connection","Could not load BankEase.\nCheck that Oracle is running, SQL scripts are installed, and app/db_config.py is correct.\n\nDetails:\n"+str(e))

if __name__=="__main__":
    try: BankEaseApp().mainloop()
    except Exception as e: messagebox.showerror("BankEase startup error",str(e))
