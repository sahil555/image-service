#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
AWS_REGION="${AWS_REGION:-ap-south-1}"
S3_BUCKET_NAME="${S3_BUCKET_NAME:-image-service-bucket}"
DYNAMODB_TABLE_NAME="${DYNAMODB_TABLE_NAME:-image-service-table}"
PORT="${PORT:-8000}"

# Usage
usage() {
    cat <<EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  uvicorn             Run the app with uvicorn (local development)
  serverless-local    Run the app with serverless-offline (local Lambda emulation)
  docker              Run the app inside Docker container
  serverless-deploy   Deploy to AWS Lambda (requires AWS credentials)
  serverless-remove   Remove AWS Lambda stack (requires AWS credentials)

Options:
  --port PORT         Port to run on (default: 8000)
  --help              Show this help message

Examples:
  $0 uvicorn                          # Run with uvicorn on port 8000
  $0 uvicorn --port 3000              # Run with uvicorn on port 3000
  $0 serverless-local                 # Run with serverless-offline
  $0 docker                           # Run with Docker compose
  $0 serverless-deploy --stage prod   # Deploy to AWS Lambda (prod stage)

EOF
    exit 1
}

# Parse arguments
COMMAND=${1:-help}
shift || true

case "$COMMAND" in
    uvicorn)
        echo -e "${GREEN}Starting app with uvicorn on port $PORT...${NC}"
        source .venv/bin/activate 2>/dev/null || true
        uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
        ;;

    serverless-local)
        echo -e "${GREEN}Starting app with serverless-offline...${NC}"
        echo -e "${YELLOW}Note: Ensure serverless and serverless-offline are installed:${NC}"
        echo "  npm install -g serverless serverless-offline serverless-python-requirements"
        echo ""
        
        if ! command -v serverless &> /dev/null; then
            echo -e "${RED}❌ serverless CLI not found. Installing...${NC}"
            npm install -g serverless serverless-offline serverless-python-requirements
        fi
        
        npm install --save-dev serverless-offline serverless-python-requirements 2>/dev/null || true
        
        export AWS_REGION="$AWS_REGION"
        export S3_BUCKET_NAME="$S3_BUCKET_NAME"
        export DYNAMODB_TABLE_NAME="$DYNAMODB_TABLE_NAME"
        
        serverless offline start --stage dev
        ;;

    docker)
        echo -e "${GREEN}Starting app with Docker Compose...${NC}"
        docker compose -f docker-compose.yml up -d --build
        echo -e "${GREEN}✓ Container started. Access at http://localhost:8000${NC}"
        echo ""
        echo "View logs:"
        echo "  docker compose logs -f image-service"
        echo ""
        echo "Stop container:"
        echo "  docker compose down"
        ;;

    serverless-deploy)
        echo -e "${GREEN}Deploying to AWS Lambda...${NC}"
        
        if ! command -v serverless &> /dev/null; then
            echo -e "${RED}❌ serverless CLI not found. Installing...${NC}"
            npm install -g serverless serverless-python-requirements
        fi
        
        npm install --save-dev serverless-python-requirements 2>/dev/null || true
        
        export AWS_REGION="$AWS_REGION"
        export S3_BUCKET_NAME="$S3_BUCKET_NAME"
        export DYNAMODB_TABLE_NAME="$DYNAMODB_TABLE_NAME"
        
        STAGE="${1:-dev}"
        echo -e "${YELLOW}Deploying to stage: $STAGE${NC}"
        serverless deploy --stage "$STAGE"
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        ;;

    serverless-remove)
        echo -e "${RED}Removing AWS Lambda stack...${NC}"
        
        STAGE="${1:-dev}"
        echo -e "${YELLOW}Removing stage: $STAGE${NC}"
        
        read -p "Are you sure you want to remove this stack? (yes/no): " confirm
        if [ "$confirm" == "yes" ]; then
            serverless remove --stage "$STAGE"
            echo -e "${GREEN}✓ Stack removed!${NC}"
        else
            echo "Cancelled."
        fi
        ;;

    serverless-info)
        echo -e "${GREEN}Serverless deployment info...${NC}"
        STAGE="${1:-dev}"
        serverless info --stage "$STAGE"
        ;;

    help|--help|-h)
        usage
        ;;

    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        usage
        ;;
esac
