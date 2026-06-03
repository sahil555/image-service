#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
AWS_REGION="${AWS_REGION:-ap-south-1}"
S3_BUCKET_NAME="${S3_BUCKET_NAME:-image-service-bucket-ap-south-1}"
DYNAMODB_TABLE_NAME="${DYNAMODB_TABLE_NAME:-image-service-table-ap-south-1}"
PORT="${PORT:-8000}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-AWS_ACCESS_KEY_ID}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-AWS_SECRET_ACCESS_KEY}"

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
        source .venv/bin/activate
        uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
        ;;

    serverless-local)
        echo -e "${GREEN}Setting ENV for serverless local...${NC}"
        python3 deployment/docker/docker_script_cred_set.py
        echo -e "${AWS_ACCESS_KEY_ID} and ${AWS_SECRET_ACCESS_KEY} set for build."
        echo -e "${GREEN}Starting app with serverless-offline...${NC}"
        echo -e "${YELLOW}Note: Ensure serverless and serverless-offline are installed:${NC}"
        echo "  installing serverless plugins may take a few minutes on first run"
        echo ""
        
        if ! command -v serverless &> /dev/null; then
            echo -e "${RED}❌ serverless CLI not found. Installing...${NC}"
            npm install -g serverless serverless-offline
        fi
        
        npm install --save-dev serverless-offline 2>/dev/null || true
        
        serverless offline start --stage dev --port 5000
        echo -e "${GREEN}✓ Serverless offline started. Access at http://localhost:5000${NC}"
        ;;

    docker)
        echo -e "${GREEN}Setting ENV for Docker image...${NC}"
        python3 deployment/docker/docker_script_cred_set.py
        echo -e "${AWS_ACCESS_KEY_ID} and ${AWS_SECRET_ACCESS_KEY} set for Docker build."
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
            npm install -g serverless serverless-offline
        fi
        
        npm install --save-dev serverless-offline 2>/dev/null || true
        
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
