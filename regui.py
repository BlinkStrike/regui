import tkinter as tk
from tkinter import ttk, messagebox, font
import redis
import threading
import time
from datetime import datetime
import json

class ModernRedisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RegUI - Modern Redis Manager")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Configure modern style
        self.setup_styles()
        
        self.redis_client = None
        self.connection_status = "Disconnected"
        self.server_info = {}
        self.monitoring_active = False
        
        # Create main layout
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def setup_styles(self):
        """Configure modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'select_bg': '#3d4043',
            'select_fg': '#ffffff',
            'accent': '#ff6b6b',
            'success': '#51cf66',
            'warning': '#ffd43b',
            'info': '#74c0fc'
        }
        
        # Configure styles
        style.configure('Modern.TFrame', background=colors['bg'])
        style.configure('Modern.TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('Modern.TButton', background=colors['select_bg'], foreground=colors['fg'])
        style.configure('Modern.TEntry', fieldbackground=colors['select_bg'], foreground=colors['fg'])
        style.configure('Treeview', background=colors['select_bg'], foreground=colors['fg'], fieldbackground=colors['select_bg'])
        style.configure('Treeview.Heading', background=colors['bg'], foreground=colors['fg'])
        
    def create_header(self):
        """Create modern header with connection controls"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Connection section
        conn_frame = tk.Frame(header_frame, bg='#2d2d2d')
        conn_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(conn_frame, text="Host:", bg='#2d2d2d', fg='white', font=('Arial', 9)).grid(row=0, column=0, padx=(0,5))
        self.host_entry = tk.Entry(conn_frame, bg='#3d4043', fg='white', insertbackground='white', width=12)
        self.host_entry.insert(0, 'localhost')
        self.host_entry.grid(row=0, column=1, padx=(0,10))
        
        tk.Label(conn_frame, text="Port:", bg='#2d2d2d', fg='white', font=('Arial', 9)).grid(row=0, column=2, padx=(0,5))
        self.port_entry = tk.Entry(conn_frame, bg='#3d4043', fg='white', insertbackground='white', width=8)
        self.port_entry.insert(0, '6379')
        self.port_entry.grid(row=0, column=3, padx=(0,10))
        
        self.connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_to_redis,
                                   bg='#51cf66', fg='white', font=('Arial', 9, 'bold'),
                                   relief='flat', padx=15)
        self.connect_btn.grid(row=0, column=4, padx=(0,5))
        
        # Status indicator
        status_frame = tk.Frame(header_frame, bg='#2d2d2d')
        status_frame.pack(side='right', padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text="● Disconnected", 
                                   bg='#2d2d2d', fg='#ff6b6b', font=('Arial', 10, 'bold'))
        self.status_label.pack()
        
    def create_main_content(self):
        """Create main dashboard content"""
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Server info and metrics
        left_panel = tk.Frame(main_frame, bg='#2d2d2d', width=300)
        left_panel.pack(side='left', fill='y', padx=(0,10))
        left_panel.pack_propagate(False)
        
        self.create_server_info_panel(left_panel)
        self.create_metrics_panel(left_panel)
        
        # Right panel - Keys and operations
        right_panel = tk.Frame(main_frame, bg='#1a1a1a')
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.create_keys_panel(right_panel)
        self.create_operations_panel(right_panel)
        
    def create_server_info_panel(self, parent):
        """Create server information panel"""
        info_frame = tk.LabelFrame(parent, text="Server Info", bg='#2d2d2d', fg='white', 
                                 font=('Arial', 10, 'bold'))
        info_frame.pack(fill='x', padx=10, pady=10)
        
        self.info_labels = {}
        info_items = ['Version', 'Uptime', 'Clients', 'Memory', 'Keys']
        
        for i, item in enumerate(info_items):
            label = tk.Label(info_frame, text=f"{item}:", bg='#2d2d2d', fg='#aaa', 
                           font=('Arial', 9), anchor='w')
            label.grid(row=i, column=0, sticky='w', padx=10, pady=2)
            
            value_label = tk.Label(info_frame, text="-", bg='#2d2d2d', fg='white', 
                                 font=('Arial', 9, 'bold'), anchor='w')
            value_label.grid(row=i, column=1, sticky='w', padx=(20,10), pady=2)
            self.info_labels[item] = value_label
            
    def create_metrics_panel(self, parent):
        """Create metrics panel"""
        metrics_frame = tk.LabelFrame(parent, text="Metrics", bg='#2d2d2d', fg='white', 
                                    font=('Arial', 10, 'bold'))
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Commands per second
        self.create_metric_card(metrics_frame, "Commands/sec", "0", "#74c0fc", 0)
        self.create_metric_card(metrics_frame, "Hit Rate", "0%", "#51cf66", 1)
        self.create_metric_card(metrics_frame, "Memory Usage", "0 MB", "#ffd43b", 2)
        
    def create_metric_card(self, parent, title, value, color, row):
        """Create individual metric card"""
        card_frame = tk.Frame(parent, bg='#3d4043')
        card_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(card_frame, text=title, bg='#3d4043', fg='#aaa', 
                             font=('Arial', 8))
        title_label.pack(anchor='w', padx=10, pady=(5,0))
        
        value_label = tk.Label(card_frame, text=value, bg='#3d4043', fg=color, 
                             font=('Arial', 12, 'bold'))
        value_label.pack(anchor='w', padx=10, pady=(0,5))
        
        setattr(self, f"metric_{title.lower().replace('/', '_').replace(' ', '_')}", value_label)
        
    def create_keys_panel(self, parent):
        """Create keys management panel"""
        keys_frame = tk.LabelFrame(parent, text="Keys Browser", bg='#2d2d2d', fg='white', 
                                 font=('Arial', 10, 'bold'))
        keys_frame.pack(fill='both', expand=True, padx=(0,0), pady=(0,10))
        
        # Search and controls
        controls_frame = tk.Frame(keys_frame, bg='#2d2d2d')
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(controls_frame, text="Search:", bg='#2d2d2d', fg='white', 
               font=('Arial', 9)).pack(side='left')
        
        self.search_entry = tk.Entry(controls_frame, bg='#3d4043', fg='white', 
                                   insertbackground='white', width=20)
        self.search_entry.pack(side='left', padx=(5,10))
        self.search_entry.bind('<KeyRelease>', self.filter_keys)
        
        refresh_btn = tk.Button(controls_frame, text="Refresh", command=self.load_keys,
                              bg='#74c0fc', fg='white', font=('Arial', 8),
                              relief='flat', padx=10)
        refresh_btn.pack(side='left', padx=5)
        
        # Keys treeview
        tree_frame = tk.Frame(keys_frame, bg='#2d2d2d')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        self.keys_tree = ttk.Treeview(tree_frame, columns=('Type', 'TTL', 'Size'), show='tree headings')
        self.keys_tree.heading('#0', text='Key', anchor='w')
        self.keys_tree.heading('Type', text='Type', anchor='w')
        self.keys_tree.heading('TTL', text='TTL', anchor='w')
        self.keys_tree.heading('Size', text='Size', anchor='w')
        
        self.keys_tree.column('#0', width=200)
        self.keys_tree.column('Type', width=80)
        self.keys_tree.column('TTL', width=80)
        self.keys_tree.column('Size', width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.keys_tree.yview)
        self.keys_tree.configure(yscrollcommand=scrollbar.set)
        
        self.keys_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.keys_tree.bind('<<TreeviewSelect>>', self.on_key_select)
        
    def create_operations_panel(self, parent):
        """Create operations panel"""
        ops_frame = tk.LabelFrame(parent, text="Key Operations", bg='#2d2d2d', fg='white', 
                                font=('Arial', 10, 'bold'))
        ops_frame.pack(fill='x', padx=(0,0), pady=0)
        
        # Value display
        value_frame = tk.Frame(ops_frame, bg='#2d2d2d')
        value_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(value_frame, text="Value:", bg='#2d2d2d', fg='white', 
               font=('Arial', 9)).pack(anchor='w')
        
        self.value_text = tk.Text(value_frame, height=6, bg='#3d4043', fg='white', 
                                insertbackground='white', font=('Consolas', 9))
        self.value_text.pack(fill='x', pady=(5,0))
        
        # Set key-value
        set_frame = tk.Frame(ops_frame, bg='#2d2d2d')
        set_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(set_frame, text="Set Key-Value:", bg='#2d2d2d', fg='white', 
               font=('Arial', 9, 'bold')).pack(anchor='w')
        
        input_frame = tk.Frame(set_frame, bg='#2d2d2d')
        input_frame.pack(fill='x', pady=(5,0))
        
        tk.Label(input_frame, text="Key:", bg='#2d2d2d', fg='white', 
               font=('Arial', 9)).grid(row=0, column=0, sticky='w')
        self.key_entry = tk.Entry(input_frame, bg='#3d4043', fg='white', 
                                insertbackground='white', width=20)
        self.key_entry.grid(row=0, column=1, padx=(5,10), sticky='ew')
        
        tk.Label(input_frame, text="Value:", bg='#2d2d2d', fg='white', 
               font=('Arial', 9)).grid(row=0, column=2, sticky='w')
        self.value_entry = tk.Entry(input_frame, bg='#3d4043', fg='white', 
                                  insertbackground='white', width=20)
        self.value_entry.grid(row=0, column=3, padx=(5,10), sticky='ew')
        
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(set_frame, bg='#2d2d2d')
        btn_frame.pack(fill='x', pady=(10,0))
        
        set_btn = tk.Button(btn_frame, text="Set", command=self.set_key,
                          bg='#51cf66', fg='white', font=('Arial', 9),
                          relief='flat', padx=15)
        set_btn.pack(side='left', padx=(0,5))
        
        del_btn = tk.Button(btn_frame, text="Delete Selected", command=self.delete_key,
                          bg='#ff6b6b', fg='white', font=('Arial', 9),
                          relief='flat', padx=15)
        del_btn.pack(side='left', padx=5)
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg='#2d2d2d', height=25)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_text = tk.Label(status_frame, text="Ready", bg='#2d2d2d', fg='#aaa', 
                                  font=('Arial', 8), anchor='w')
        self.status_text.pack(side='left', padx=10, pady=5)
        
        time_label = tk.Label(status_frame, text="", bg='#2d2d2d', fg='#aaa', 
                            font=('Arial', 8))
        time_label.pack(side='right', padx=10, pady=5)
        
        def update_time():
            time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, update_time)
        
        update_time()

    def connect_to_redis(self):
        """Connect to Redis server with modern UI feedback"""
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        
        self.status_text.config(text="Connecting...")
        self.connect_btn.config(text="Connecting...", state='disabled')
        
        def connect_thread():
            try:
                self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
                self.redis_client.ping()
                
                # Update UI on successful connection
                self.root.after(0, self.on_connection_success)
                
            except Exception as e:
                self.root.after(0, lambda: self.on_connection_error(str(e)))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def on_connection_success(self):
        """Handle successful connection"""
        self.connection_status = "Connected"
        self.status_label.config(text="● Connected", fg='#51cf66')
        self.status_text.config(text="Connected to Redis server")
        self.connect_btn.config(text="Disconnect", state='normal', bg='#ff6b6b',
                              command=self.disconnect_from_redis)
        self.monitoring_active = True
        self.load_keys()
        self.update_server_info()
    
    def on_connection_error(self, error):
        """Handle connection error"""
        self.status_text.config(text=f"Connection failed: {error}")
        self.connect_btn.config(text="Connect", state='normal')
        messagebox.showerror("Connection Failed", error)
    
    def disconnect_from_redis(self):
        """Disconnect from Redis server"""
        self.redis_client = None
        self.connection_status = "Disconnected"
        self.monitoring_active = False
        self.status_label.config(text="● Disconnected", fg='#ff6b6b')
        self.status_text.config(text="Disconnected from Redis server")
        self.connect_btn.config(text="Connect", bg='#51cf66', command=self.connect_to_redis)
        
        # Clear data
        self.keys_tree.delete(*self.keys_tree.get_children())
        self.value_text.delete(1.0, tk.END)
        
        # Reset info labels
        for label in self.info_labels.values():
            label.config(text="-")
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        def monitor():
            while True:
                if self.monitoring_active and self.redis_client:
                    try:
                        self.root.after(0, self.update_server_info)
                        self.root.after(0, self.update_metrics)
                    except:
                        pass
                time.sleep(2)  # Update every 2 seconds
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_server_info(self):
        """Update server information panel"""
        if not self.redis_client:
            return
            
        try:
            info = self.redis_client.info()
            
            # Update server info
            self.info_labels['Version'].config(text=info.get('redis_version', '-'))
            
            uptime = info.get('uptime_in_seconds', 0)
            uptime_str = f"{uptime // 86400}d {(uptime % 86400) // 3600}h"
            self.info_labels['Uptime'].config(text=uptime_str)
            
            self.info_labels['Clients'].config(text=str(info.get('connected_clients', 0)))
            
            memory_mb = info.get('used_memory', 0) / (1024 * 1024)
            self.info_labels['Memory'].config(text=f"{memory_mb:.1f} MB")
            
            # Count keys
            db_keys = 0
            for key in info.keys():
                if key.startswith('db'):
                    db_info = info[key]
                    if 'keys=' in db_info:
                        keys_count = int(db_info.split('keys=')[1].split(',')[0])
                        db_keys += keys_count
            
            self.info_labels['Keys'].config(text=str(db_keys))
            
        except Exception as e:
            print(f"Error updating server info: {e}")
    
    def update_metrics(self):
        """Update metrics panel"""
        if not self.redis_client:
            return
            
        try:
            info = self.redis_client.info()
            
            # Commands per second (approximation)
            total_commands = info.get('total_commands_processed', 0)
            uptime = info.get('uptime_in_seconds', 1)
            cmd_per_sec = total_commands / uptime if uptime > 0 else 0
            self.metric_commands_sec.config(text=f"{cmd_per_sec:.1f}")
            
            # Hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            self.metric_hit_rate.config(text=f"{hit_rate:.1f}%")
            
            # Memory usage
            memory_mb = info.get('used_memory', 0) / (1024 * 1024)
            self.metric_memory_usage.config(text=f"{memory_mb:.1f} MB")
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def load_keys(self):
        """Load keys into the tree view"""
        if not self.redis_client:
            self.status_text.config(text="Please connect to Redis first")
            return
        
        self.status_text.config(text="Loading keys...")
        
        def load_thread():
            try:
                keys = self.redis_client.keys('*')
                self.root.after(0, lambda: self.populate_keys_tree(keys))
            except Exception as e:
                self.root.after(0, lambda: self.status_text.config(text=f"Error loading keys: {e}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def populate_keys_tree(self, keys):
        """Populate the keys tree view"""
        # Clear existing items
        self.keys_tree.delete(*self.keys_tree.get_children())
        
        for key in keys:
            try:
                # Get key type
                key_type = self.redis_client.type(key)
                
                # Get TTL
                ttl = self.redis_client.ttl(key)
                ttl_str = str(ttl) if ttl > 0 else "∞"
                
                # Get size (approximation)
                size = "1"  # Default for simple types
                if key_type == 'list':
                    size = str(self.redis_client.llen(key))
                elif key_type == 'set':
                    size = str(self.redis_client.scard(key))
                elif key_type == 'zset':
                    size = str(self.redis_client.zcard(key))
                elif key_type == 'hash':
                    size = str(self.redis_client.hlen(key))
                
                self.keys_tree.insert('', 'end', text=key, values=(key_type, ttl_str, size))
                
            except Exception as e:
                print(f"Error processing key {key}: {e}")
        
        self.status_text.config(text=f"Loaded {len(keys)} keys")
    
    def on_key_select(self, event):
        """Handle key selection in tree view"""
        selection = self.keys_tree.selection()
        if selection:
            key = self.keys_tree.item(selection[0])['text']
            self.display_key_value(key)
    
    def display_key_value(self, key):
        """Display the value of selected key"""
        if not self.redis_client:
            return
            
        try:
            key_type = self.redis_client.type(key)
            self.value_text.delete(1.0, tk.END)
            
            if key_type == 'string':
                value = self.redis_client.get(key)
                self.value_text.insert(tk.END, str(value))
            elif key_type == 'list':
                values = self.redis_client.lrange(key, 0, -1)
                self.value_text.insert(tk.END, json.dumps(values, indent=2))
            elif key_type == 'set':
                values = list(self.redis_client.smembers(key))
                self.value_text.insert(tk.END, json.dumps(values, indent=2))
            elif key_type == 'zset':
                values = self.redis_client.zrange(key, 0, -1, withscores=True)
                self.value_text.insert(tk.END, json.dumps(values, indent=2))
            elif key_type == 'hash':
                values = self.redis_client.hgetall(key)
                self.value_text.insert(tk.END, json.dumps(values, indent=2))
            else:
                self.value_text.insert(tk.END, f"Unsupported type: {key_type}")
                
        except Exception as e:
            self.value_text.insert(tk.END, f"Error: {str(e)}")
    
    def filter_keys(self, event):
        """Filter keys based on search input"""
        search_term = self.search_entry.get().lower()
        
        # Show/hide items based on search
        for item in self.keys_tree.get_children():
            key = self.keys_tree.item(item)['text'].lower()
            if search_term in key:
                self.keys_tree.reattach(item, '', 'end')
            else:
                self.keys_tree.detach(item)
    
    def set_key(self):
        """Set a key-value pair"""
        if not self.redis_client:
            self.status_text.config(text="Please connect to Redis first")
            return
            
        key = self.key_entry.get().strip()
        value = self.value_entry.get().strip()
        
        if not key or not value:
            messagebox.showwarning("Input Error", "Key and Value cannot be empty")
            return
        
        try:
            self.redis_client.set(key, value)
            self.status_text.config(text=f"Set key '{key}' successfully")
            self.key_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)
            self.load_keys()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set key: {str(e)}")
    
    def delete_key(self):
        """Delete selected key"""
        if not self.redis_client:
            self.status_text.config(text="Please connect to Redis first")
            return
            
        selection = self.keys_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a key to delete")
            return
        
        key = self.keys_tree.item(selection[0])['text']
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete key '{key}'?"):
            try:
                self.redis_client.delete(key)
                self.status_text.config(text=f"Deleted key '{key}' successfully")
                self.value_text.delete(1.0, tk.END)
                self.load_keys()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete key: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernRedisGUI(root)
    root.mainloop()
