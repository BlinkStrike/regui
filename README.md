# RegUI - Modern Redis Manager

A modern, dark-themed Redis GUI manager built with Python and Tkinter, featuring a dashboard-style interface similar to professional Redis monitoring tools.

## Features

### 🎨 Modern UI
- **Dark Theme**: Professional dark interface with modern styling
- **Dashboard Layout**: Clean, organized layout with dedicated panels
- **Real-time Monitoring**: Live server metrics and statistics
- **Responsive Design**: Adaptive layout that works on different screen sizes

### 🔧 Core Functionality
- **Connection Management**: Easy Redis server connection with visual status indicators
- **Key Browser**: Advanced tree view with key type, TTL, and size information
- **Multi-type Support**: Handle strings, lists, sets, sorted sets, and hashes
- **Search & Filter**: Real-time key filtering and search functionality
- **CRUD Operations**: Create, read, update, and delete Redis keys

### 📊 Monitoring & Metrics
- **Server Information**: Version, uptime, connected clients, memory usage
- **Performance Metrics**: Commands per second, hit rate, memory usage
- **Real-time Updates**: Automatic refresh of server statistics
- **Connection Status**: Visual connection status with color indicators

## Installation

1. **Clone or download** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python regui.py
   ```

## Usage

### Connecting to Redis
1. Enter your Redis server **host** and **port** in the header
2. Click **Connect** to establish connection
3. The status indicator will show green when connected

### Managing Keys
- **Browse Keys**: Use the tree view to see all keys with their types and metadata
- **Search**: Use the search box to filter keys in real-time
- **View Values**: Click on any key to view its value in the operations panel
- **Add Keys**: Use the "Set Key-Value" section to create new keys
- **Delete Keys**: Select a key and click "Delete Selected"

### Monitoring
- **Server Info Panel**: Shows Redis version, uptime, clients, memory, and key count
- **Metrics Panel**: Displays commands per second, hit rate, and memory usage
- **Auto-refresh**: Metrics update automatically every 2 seconds when connected

## Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Connection Controls + Status Indicator              │
├─────────────────┬───────────────────────────────────────────┤
│ Server Info     │ Keys Browser                              │
│ - Version       │ - Search/Filter                           │
│ - Uptime        │ - Tree View (Key, Type, TTL, Size)       │
│ - Clients       │                                           │
│ - Memory        │                                           │
│ - Keys          │                                           │
├─────────────────┤                                           │
│ Metrics         │                                           │
│ - Commands/sec  │                                           │
│ - Hit Rate      │                                           │
│ - Memory Usage  │                                           │
├─────────────────┼───────────────────────────────────────────┤
│                 │ Key Operations                            │
│                 │ - Value Display                           │
│                 │ - Set Key-Value                           │
│                 │ - Action Buttons                          │
├─────────────────┴───────────────────────────────────────────┤
│ Status Bar: Current Status + Timestamp                      │
└─────────────────────────────────────────────────────────────┘
```

## Color Scheme

- **Background**: Dark gray (#1a1a1a, #2d2d2d)
- **Text**: White (#ffffff) and light gray (#aaa)
- **Accent Colors**:
  - Success: Green (#51cf66)
  - Error: Red (#ff6b6b)
  - Info: Blue (#74c0fc)
  - Warning: Yellow (#ffd43b)

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- redis-py library
- Redis server (local or remote)

## Advanced Features

- **Threaded Operations**: Non-blocking connection and key loading
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Data Type Support**: Proper handling of all Redis data types
- **Memory Efficient**: Optimized for handling large numbers of keys
- **Professional UI**: Modern interface suitable for production environments

## Future Enhancements

Based on the features.md roadmap:
- SSH Tunnel/SSL/Sentinel support
- Command-line mode
- Slow logs monitoring
- Import/export functionality
- Pub/Sub support
- Monaco Editor integration
- Connection profiles

---

**RegUI** - Making Redis management modern and intuitive.
