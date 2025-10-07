#!/bin/bash
# Quick PostgreSQL setup script for testing Toyota Virtual Training app
# This script helps you set up a local PostgreSQL database for testing

set -e  # Exit on error

echo "========================================================================"
echo "PostgreSQL Test Setup for Toyota Virtual Training"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DB_NAME="toyota_training_test"
DB_USER="toyota_user"
DB_PASSWORD=""
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is installed
echo "Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL is installed"
    PSQL_VERSION=$(psql --version)
    echo "  $PSQL_VERSION"
else
    echo -e "${RED}✗${NC} PostgreSQL is not installed"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS:   brew install postgresql@15"
    echo "  Ubuntu:  sudo apt install postgresql postgresql-contrib"
    echo "  Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

# Check if PostgreSQL is running
echo ""
echo "Checking if PostgreSQL is running..."
if pg_isready -h localhost -p 5432 &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL is not running"
    echo ""
    echo "Start PostgreSQL:"
    echo "  macOS:   brew services start postgresql@15"
    echo "  Linux:   sudo systemctl start postgresql"
    echo ""
    read -p "Would you like to try starting it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start postgresql@15
        else
            sudo systemctl start postgresql
        fi
        sleep 2
        if pg_isready -h localhost -p 5432 &> /dev/null; then
            echo -e "${GREEN}✓${NC} PostgreSQL is now running"
        else
            echo -e "${RED}✗${NC} Failed to start PostgreSQL"
            exit 1
        fi
    else
        echo "Please start PostgreSQL and run this script again"
        exit 1
    fi
fi

# Prompt for database configuration
echo ""
echo "========================================================================"
echo "Database Configuration"
echo "========================================================================"
echo ""
echo "Default values (press Enter to accept):"
echo ""

read -p "Database name [$DB_NAME]: " input
DB_NAME="${input:-$DB_NAME}"

read -p "Database user [$DB_USER]: " input
DB_USER="${input:-$DB_USER}"

# Password is required
while [ -z "$DB_PASSWORD" ]; do
    read -sp "Database password (required): " DB_PASSWORD
    echo
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${RED}Password cannot be empty${NC}"
    fi
done

read -p "Database host [$DB_HOST]: " input
DB_HOST="${input:-$DB_HOST}"

read -p "Database port [$DB_PORT]: " input
DB_PORT="${input:-$DB_PORT}"

# Create database and user
echo ""
echo "========================================================================"
echo "Creating Database and User"
echo "========================================================================"
echo ""

# Check if user exists
if psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${YELLOW}⚠${NC} User '$DB_USER' already exists"
    read -p "Update password? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql postgres -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>&1 | grep -v "^ALTER ROLE$" || true
        echo -e "${GREEN}✓${NC} Updated password for user '$DB_USER'"
    fi
else
    psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>&1 | grep -v "^CREATE ROLE$" || true
    echo -e "${GREEN}✓${NC} Created user '$DB_USER'"
fi

# Check if database exists
if psql postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${YELLOW}⚠${NC} Database '$DB_NAME' already exists"
    read -p "Drop and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql postgres -c "DROP DATABASE $DB_NAME;" 2>&1 | grep -v "^DROP DATABASE$" || true
        psql postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>&1 | grep -v "^CREATE DATABASE$" || true
        echo -e "${GREEN}✓${NC} Recreated database '$DB_NAME'"
    fi
else
    psql postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>&1 | grep -v "^CREATE DATABASE$" || true
    echo -e "${GREEN}✓${NC} Created database '$DB_NAME'"
fi

# Grant privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>&1 | grep -v "^GRANT$" || true
echo -e "${GREEN}✓${NC} Granted privileges to '$DB_USER'"

# Create .env file
echo ""
echo "========================================================================"
echo "Creating .env File"
echo "========================================================================"
echo ""

ENV_FILE=".env.postgres"
cat > "$ENV_FILE" << EOF
# PostgreSQL Configuration for Testing
# Generated by setup_postgres_test.sh on $(date)

DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
EOF

echo -e "${GREEN}✓${NC} Created $ENV_FILE"
echo ""
echo "To use these settings, run:"
echo "  export \$(cat $ENV_FILE | xargs)"
echo ""

# Ask if user wants to test connection now
read -p "Would you like to test the connection now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "========================================================================"
    echo "Testing Connection"
    echo "========================================================================"
    echo ""
    
    # Export environment variables
    export DB_NAME
    export DB_USER
    export DB_PASSWORD
    export DB_HOST
    export DB_PORT
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Install dependencies
    echo "Installing/updating dependencies..."
    pip install -q -r requirements.txt
    
    # Run test script
    python test_postgres_connection.py
fi

echo ""
echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Load environment variables:"
echo "   export \$(cat $ENV_FILE | xargs)"
echo ""
echo "2. Run migrations:"
echo "   python manage.py migrate"
echo ""
echo "3. Create superuser:"
echo "   python manage.py createsuperuser"
echo ""
echo "4. Start development server:"
echo "   python manage.py runserver"
echo ""
echo "To switch back to SQLite, simply unset the environment variables:"
echo "   unset DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT"
echo ""
echo "For more information, see: POSTGRESQL_TESTING_GUIDE.md"
echo ""

