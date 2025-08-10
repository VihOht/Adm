# 📊 Financial Data Management System

## 🎯 Overview

This system provides comprehensive import/export functionality for financial data including expenses, incomes, and their respective categories. Users can backup their data, migrate between systems, or bulk import sample data.

## 🔧 Management Command

### Basic Usage

```bash
# Export user data
python manage.py financial_data export --file backup.json --user username

# Import data for a user
python manage.py financial_data import --file backup.json --user username

# Import with clearing existing data
python manage.py financial_data import --file backup.json --user username --clear
```

### Command Options

| Option | Description | Required |
|--------|-------------|----------|
| `action` | `import` or `export` | ✅ Yes |
| `--file` | Path to JSON file | ✅ Yes |
| `--user` | Username (required for import) | ⚠️ Import only |
| `--clear` | Clear existing data before import | ❌ Optional |

### Examples

```bash
# Export all data for a specific user
python manage.py financial_data export --file user_backup_2025.json --user john_doe

# Export all users' data
python manage.py financial_data export --file all_users_backup.json

# Import sample data for testing
python manage.py financial_data import --file sample_financial_data.json --user test_user

# Import and replace all existing data
python manage.py financial_data import --file new_data.json --user john_doe --clear
```

## 🌐 Web Interface

### Download Feature

Users can download their financial data directly from the web interface:

1. **Access**: Navigate to Finance Manager Dashboard
2. **Download**: Click "Exportar Dados" button in the top-right corner
3. **File**: Downloads as `financial_data_username_YYYYMMDD_HHMMSS.json`

### Upload Feature

Users can import financial data directly from the web interface:

1. **Access**: Navigate to Finance Manager Dashboard
2. **Import**: Click "Importar Dados" button in the top-right corner
3. **Select File**: Choose a JSON file to upload
4. **Preview**: View the data summary before importing
5. **Options**: Choose to clear existing data or merge with current data
6. **Import**: Click "Importar Dados" to process the file

### URL Endpoint

**Export:**
```
GET /finance/export/
```

**Import:**
```
POST /finance/import/
```

- **Authentication**: Login required for both endpoints
- **Export Response**: JSON file download with `Content-Type: application/json`
- **Import Request**: Multipart form data with file upload
- **File Name**: Automatically generated with timestamp (export only)

## 📄 JSON Data Structure

### Single User Export Format

```json
{
  "exported_at": "2025-08-09T10:00:00",
  "username": "sample_user",
  "expense_categories": [
    {
      "name": "Food & Dining",
      "description": "Restaurants, groceries, and food delivery",
      "color": "#FF6B6B"
    }
  ],
  "income_categories": [
    {
      "name": "Salary",
      "description": "Monthly salary from work",
      "color": "#2ECC71"
    }
  ],
  "expenses": [
    {
      "category": "Food & Dining",
      "spent_at": "2025-08-01",
      "description": "Grocery shopping",
      "detailed_description": "Weekly grocery shopping at supermarket",
      "amount": 15000,
      "created_at": "2025-08-01T18:30:00"
    }
  ],
  "incomes": [
    {
      "category": "Salary",
      "received_at": "2025-08-01",
      "description": "Monthly salary",
      "detailed_description": "August 2025 salary payment",
      "amount": 500000,
      "created_at": "2025-08-01T09:00:00"
    }
  ]
}
```

### Multi-User Export Format

```json
{
  "exported_at": "2025-08-09T10:00:00",
  "users": [
    {
      "username": "user1",
      "expense_categories": [...],
      "income_categories": [...],
      "expenses": [...],
      "incomes": [...]
    },
    {
      "username": "user2",
      "expense_categories": [...],
      "income_categories": [...],
      "expenses": [...],
      "incomes": [...]
    }
  ]
}
```

## 💰 Data Fields

### Categories (Expense & Income)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | String | Category name | "Food & Dining" |
| `description` | String | Detailed description | "Restaurants, groceries, and food delivery" |
| `color` | String | Hex color code | "#FF6B6B" |

### Transactions (Expenses & Incomes)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `category` | String | Category name (null if none) | "Food & Dining" |
| `spent_at/received_at` | Date | Transaction date | "2025-08-01" |
| `description` | String | Short description | "Grocery shopping" |
| `detailed_description` | String | Detailed description | "Weekly grocery shopping at supermarket" |
| `amount` | Integer | Amount in cents | 15000 (=$150.00) |
| `created_at` | DateTime | Record creation timestamp | "2025-08-01T18:30:00" |

## 🔄 Import Process

### Data Validation

- ✅ **Date Format**: YYYY-MM-DD format required
- ✅ **Category Matching**: Categories created if they don't exist
- ✅ **User Validation**: User must exist before import
- ✅ **Duplicate Prevention**: Unique constraints prevent category duplicates
- ✅ **Amount Format**: Expects integer values (cents)

### Import Behavior

1. **Categories First**: Creates expense and income categories
2. **Transactions Second**: Creates expenses and incomes with category links
3. **Error Handling**: Skips invalid records, continues processing
4. **Atomic Operations**: Uses database transactions for consistency
5. **Clear Option**: Optionally removes existing data before import

## 🛡️ Security Features

- **User Isolation**: Users can only export/import their own data
- **Authentication Required**: Login required for all operations
- **Data Validation**: Comprehensive input validation
- **Error Handling**: Graceful error handling with informative messages

## 📊 Sample Data

The system includes `sample_financial_data.json` with:

- ✅ 5 Expense Categories (Food, Transportation, Entertainment, Utilities, Healthcare)
- ✅ 4 Income Categories (Salary, Freelance, Investment, Gift)
- ✅ 5 Sample Expenses with realistic amounts and descriptions
- ✅ 3 Sample Incomes with different categories and amounts
- ✅ Color-coded categories for visual organization

## 🚀 Usage Scenarios

### 1. **Data Backup**
```bash
# Regular backup
python manage.py financial_data export --file "backup_$(date +%Y%m%d).json" --user $USERNAME
```

### 2. **User Onboarding**
```bash
# Import sample data for new users
python manage.py financial_data import --file sample_financial_data.json --user new_user
```

### 3. **Data Migration**
```bash
# Export from old system
python manage.py financial_data export --file migration_data.json --user old_user

# Import to new system
python manage.py financial_data import --file migration_data.json --user new_user --clear
```

### 4. **Testing**
```bash
# Load test data
python manage.py financial_data import --file sample_financial_data.json --user test_user --clear
```

## 📋 File Management

### File Locations

- **Sample Data**: `sample_financial_data.json` (root directory)
- **Management Command**: `finance_manager/management/commands/financial_data.py`
- **View Function**: `finance_manager/views.py::export_financial_data`
- **URL Pattern**: `finance_manager/urls.py`

### File Naming Convention

**Downloaded Files**: `financial_data_[username]_[YYYYMMDD]_[HHMMSS].json`

Example: `financial_data_john_doe_20250809_143052.json`

## 🎨 UI Integration

The download button is integrated into the Finance Manager Dashboard:

- **Location**: Top-right corner of the dashboard
- **Style**: Outline button with download icon
- **Behavior**: Direct download, no page refresh
- **Responsive**: Adapts to mobile screens

## 🔍 Troubleshooting

### Common Issues

1. **User Not Found**: Ensure user exists before importing
2. **Invalid JSON**: Validate JSON format before importing
3. **Date Format Error**: Use YYYY-MM-DD format for dates
4. **Permission Error**: Ensure proper file permissions for export location
5. **Category Conflicts**: Use `--clear` flag to reset categories

### Debug Commands

```bash
# Test export functionality
python manage.py financial_data export --file test_export.json --user test_user

# Validate import file
python -m json.tool your_file.json

# Check user exists
python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username='your_username').exists())"
```

This comprehensive system provides robust financial data management with both programmatic and web-based interfaces! 🎉
