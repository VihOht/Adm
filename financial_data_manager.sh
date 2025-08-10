#!/bin/bash

# 📊 Financial Data Management - Example Usage Script
# This script demonstrates how to use the financial data management system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"

echo -e "${BLUE}📊 Financial Data Management System${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Virtual environment not found at $PYTHON_CMD${NC}"
    echo -e "${YELLOW}Please set up your Python environment first${NC}"
    exit 1
fi

# Function to show help
show_help() {
    echo -e "${GREEN}Available Operations:${NC}"
    echo ""
    echo -e "${YELLOW}1. Export user data:${NC}"
    echo "   $0 export <username> [output_file]"
    echo ""
    echo -e "${YELLOW}2. Import user data:${NC}"
    echo "   $0 import <username> <input_file> [--clear]"
    echo ""
    echo -e "${YELLOW}3. Load sample data:${NC}"
    echo "   $0 sample <username>"
    echo ""
    echo -e "${YELLOW}4. Backup all users:${NC}"
    echo "   $0 backup"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "   $0 export john_doe"
    echo "   $0 import jane_doe backup.json"
    echo "   $0 import jane_doe backup.json --clear"
    echo "   $0 sample test_user"
    echo "   $0 backup"
    echo ""
}

# Function to export user data
export_data() {
    local username="$1"
    local output_file="${2:-financial_data_${username}_$(date +%Y%m%d_%H%M%S).json}"
    
    echo -e "${BLUE}📤 Exporting data for user: $username${NC}"
    
    if $PYTHON_CMD manage.py financial_data export --file "$output_file" --user "$username"; then
        echo -e "${GREEN}✅ Export successful!${NC}"
        echo -e "${GREEN}📁 File saved as: $output_file${NC}"
        
        # Show file size
        if [ -f "$output_file" ]; then
            local size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
            echo -e "${GREEN}📊 File size: ${size} bytes${NC}"
        fi
    else
        echo -e "${RED}❌ Export failed!${NC}"
        return 1
    fi
}

# Function to import user data
import_data() {
    local username="$1"
    local input_file="$2"
    local clear_flag="$3"
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ Input file not found: $input_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📥 Importing data for user: $username${NC}"
    echo -e "${BLUE}📁 From file: $input_file${NC}"
    
    local cmd="$PYTHON_CMD manage.py financial_data import --file $input_file --user $username"
    if [ "$clear_flag" = "--clear" ]; then
        cmd="$cmd --clear"
        echo -e "${YELLOW}⚠️  Clearing existing data first...${NC}"
    fi
    
    if $cmd; then
        echo -e "${GREEN}✅ Import successful!${NC}"
    else
        echo -e "${RED}❌ Import failed!${NC}"
        return 1
    fi
}

# Function to load sample data
load_sample() {
    local username="$1"
    
    if [ ! -f "sample_financial_data.json" ]; then
        echo -e "${RED}❌ Sample data file not found: sample_financial_data.json${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📋 Loading sample data for user: $username${NC}"
    
    if $PYTHON_CMD manage.py financial_data import --file sample_financial_data.json --user "$username" --clear; then
        echo -e "${GREEN}✅ Sample data loaded successfully!${NC}"
        echo -e "${GREEN}📊 Loaded: 5 expense categories, 4 income categories, 5 expenses, 3 incomes${NC}"
    else
        echo -e "${RED}❌ Failed to load sample data!${NC}"
        return 1
    fi
}

# Function to backup all users
backup_all() {
    local backup_file="all_users_backup_$(date +%Y%m%d_%H%M%S).json"
    
    echo -e "${BLUE}💾 Creating backup of all users${NC}"
    
    if $PYTHON_CMD manage.py financial_data export --file "$backup_file"; then
        echo -e "${GREEN}✅ Backup successful!${NC}"
        echo -e "${GREEN}📁 File saved as: $backup_file${NC}"
        
        # Show file size
        if [ -f "$backup_file" ]; then
            local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
            echo -e "${GREEN}📊 File size: ${size} bytes${NC}"
        fi
    else
        echo -e "${RED}❌ Backup failed!${NC}"
        return 1
    fi
}

# Function to check if user exists
check_user() {
    local username="$1"
    
    if ! $PYTHON_CMD manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
exists = User.objects.filter(username='$username').exists()
if not exists:
    print('User $username does not exist')
    exit(1)
" 2>/dev/null; then
        echo -e "${RED}❌ User '$username' does not exist${NC}"
        echo -e "${YELLOW}💡 Create the user first or check the username${NC}"
        return 1
    fi
}

# Main script logic
case "$1" in
    "export")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Username required for export${NC}"
            echo "Usage: $0 export <username> [output_file]"
            exit 1
        fi
        check_user "$2" && export_data "$2" "$3"
        ;;
    "import")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}❌ Username and input file required for import${NC}"
            echo "Usage: $0 import <username> <input_file> [--clear]"
            exit 1
        fi
        check_user "$2" && import_data "$2" "$3" "$4"
        ;;
    "sample")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Username required for sample data${NC}"
            echo "Usage: $0 sample <username>"
            exit 1
        fi
        check_user "$2" && load_sample "$2"
        ;;
    "backup")
        backup_all
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown operation: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
