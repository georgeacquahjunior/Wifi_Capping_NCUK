# WiFi Capping System - NCUK

A comprehensive WiFi usage monitoring and capping system with admin dashboard, usage reports, and data visualization capabilities.

## Features

### Admin Features
- **Dashboard**: Real-time overview of WiFi usage statistics
- **Usage Reports**: Detailed user usage analysis with export functionality
- **Data Visualization**: Interactive charts and graphs for usage trends
- **User Management**: Monitor user activities and data consumption

### Data Visualization
- Daily usage overview charts
- Data usage trends (bar charts)
- Session count trends (line charts)
- Top users by data usage
- Usage distribution (doughnut charts)

### Reporting Capabilities
- User usage summary tables
- CSV export functionality
- Real-time data updates
- Historical usage tracking

## Quick Start

### Automated Setup
```bash
chmod +x run.sh
./run.sh
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/georgeacquahjunior/Wifi_Capping_NCUK.git
cd Wifi_Capping_NCUK
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:5001`

## Default Login Credentials

- **Admin**: `admin` / `admin123`
- **Demo Users**: `user1` / `password`, `user2` / `password`

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Chart.js
- **Authentication**: Flask-Login
- **Data Visualization**: Chart.js with custom charts

## Database Models

- **User**: User accounts with admin privileges
- **UsageRecord**: WiFi usage tracking with bytes used, session times, and IP addresses

## Security Notes

- Change default passwords in production
- Update the secret key in production
- Consider using a more robust database for production use

## Development

The application includes sample data for demonstration purposes. In production, integrate with your network infrastructure to collect real usage data.

## License

This project is for educational and demonstration purposes.
