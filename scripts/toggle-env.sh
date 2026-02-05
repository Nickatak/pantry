#!/bin/bash

# Environment Toggle Script
# This script manages symlinks between .env and environment-specific files (.env.dev, .env.prod)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_DEV="$PROJECT_ROOT/.env.dev"
ENV_PROD="$PROJECT_ROOT/.env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    cat << EOF
${YELLOW}Usage: ./scripts/toggle-env.sh [OPTION]${NC}

Manage environment file symlinks between development and production.

OPTIONS:
    dev         Link .env to .env.dev
    prod        Link .env to .env.prod
    current     Show which environment is currently active
    status      Show symlink and file status
    help        Display this help message

EXAMPLE:
    ./scripts/toggle-env.sh dev      # Switch to development environment
    ./scripts/toggle-env.sh prod     # Switch to production environment
    ./scripts/toggle-env.sh current  # Check current environment

EOF
}

# Function to check if files exist
check_files() {
    if [ ! -f "$ENV_DEV" ]; then
        echo -e "${RED}Error: $ENV_DEV does not exist${NC}"
        echo -e "${YELLOW}Please create .env.dev or copy from .env.example${NC}"
        exit 1
    fi

    if [ ! -f "$ENV_PROD" ]; then
        echo -e "${RED}Error: $ENV_PROD does not exist${NC}"
        echo -e "${YELLOW}Please create .env.prod or copy from .env.example${NC}"
        exit 1
    fi
}

# Function to create symlink
create_symlink() {
    local target=$1
    local target_name=$(basename "$target")

    # Remove existing .env if it's a symlink or file
    if [ -L "$ENV_FILE" ]; then
        rm "$ENV_FILE"
        echo -e "${GREEN}Removed existing .env symlink${NC}"
    elif [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Warning: $ENV_FILE exists as a regular file, not a symlink${NC}"
        read -p "Replace with symlink to $target_name? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm "$ENV_FILE"
        else
            echo -e "${RED}Operation cancelled${NC}"
            exit 1
        fi
    fi

    # Create new symlink
    ln -s "$target" "$ENV_FILE"
    echo -e "${GREEN}✓ .env now points to $target_name${NC}"
}

# Function to show current environment
show_current() {
    if [ -L "$ENV_FILE" ]; then
        local target=$(readlink "$ENV_FILE")
        local target_name=$(basename "$target")
        echo -e "${GREEN}Current environment: $target_name${NC}"
    elif [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}.env exists as a regular file (not a symlink)${NC}"
    else
        echo -e "${RED}.env does not exist${NC}"
    fi
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Environment Files Status:${NC}"

    echo -n ".env.dev:  "
    [ -f "$ENV_DEV" ] && echo -e "${GREEN}✓ exists${NC}" || echo -e "${RED}✗ missing${NC}"

    echo -n ".env.prod: "
    [ -f "$ENV_PROD" ] && echo -e "${GREEN}✓ exists${NC}" || echo -e "${RED}✗ missing${NC}"

    echo -n ".env:      "
    if [ -L "$ENV_FILE" ]; then
        local target=$(readlink "$ENV_FILE")
        echo -e "${GREEN}✓ symlink → $(basename "$target")${NC}"
    elif [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠ regular file (not symlink)${NC}"
    else
        echo -e "${RED}✗ missing${NC}"
    fi
}

# Main logic
case "${1:-help}" in
    dev)
        check_files
        create_symlink "$ENV_DEV"
        echo -e "${GREEN}Development environment activated${NC}"
        ;;
    prod)
        check_files
        create_symlink "$ENV_PROD"
        echo -e "${GREEN}Production environment activated${NC}"
        ;;
    current)
        show_current
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        usage
        exit 1
        ;;
esac
