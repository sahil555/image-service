# Image Service - Comprehensive Project Overview

## Table of Contents
1. [Architecture & Design](#architecture--design)
2. [Design Patterns](#design-patterns)
3. [Best Practices Implemented](#best-practices-implemented)
4. [Technology Stack](#technology-stack)
5. [API Design](#api-design)
6. [Key Implementation Details](#key-implementation-details)
7. [Enhancements & Trade-offs](#enhancements--trade-offs)
8. [Interview Talking Points](#interview-talking-points)

---

## Architecture & Design

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      API Gateway / ALB                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   Lambda / ECS                   Serverless
        │                             │
        └──────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │      FastAPI Application   │
         │  (Stateless HTTP Server)   │
         └─────────────┬──────────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
     │         ┌───────▼────────┐        │
     │         │   Logging      │        │
     │         │ (JSON Streams) │        │
     │         └────────────────┘        │
     │                 │                 │
┌────▼────┐    ┌───────┴────────┐    ┌──▼──┐
│   S3    │    │   DynamoDB     │    │Auth │
│ Images  │    │   Metadata     │    │(IAM)│
└─────────┘    └────────────────┘    └─────┘
```

### Service Layers

```
┌─────────────────────────────────────┐
│     API Layer (Routes)              │
│  - Input validation                 │
│  - HTTP response formatting         │
│  - Exception handling               │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│    Service Layer (Business Logic)   │
│  - Upload/download orchestration    │
│  - Metadata enrichment              │
│  - Cross-resource coordination      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  Repository/Data Access Layer       │
│  - Database abstraction             │
│  - Query logic                      │
│  - Data transformation              │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  Infrastructure Layer               │
│  - AWS SDK (boto3)                  │
│  - External services                │
└─────────────────────────────────────┘
```

---

## Design Patterns

### 1. **Repository Pattern**
**Purpose:** Abstract data access logic from business logic

**Implementation:** `app/repositories/image_repository.py`
```python
class ImageRepository:
    @staticmethod
    def create_image(metadata: dict):
        # Encapsulates DynamoDB put_item logic
    
    @staticmethod
    def get_image(image_id: str):
        # Encapsulates DynamoDB get_item logic
```

**Benefits:**
- Easy to swap storage backends (DynamoDB → PostgreSQL)
- Simplified testing with mocks
- Single responsibility principle
- Centralized query logic

**Trade-offs:**
- Additional abstraction layer (minimal performance impact)
- May seem overkill for simple CRUD operations

---

### 2. **Service Layer / Facade Pattern**
**Purpose:** Orchestrate complex business logic across repositories and services

**Implementation:** `app/services/image_service.py`
```python
class ImageService:
    @staticmethod
    async def upload_image(file, metadata: dict):
        # Coordinates: S3 upload → DynamoDB save → presigned URL generation
        image_id, s3_key = await StorageService.upload_image(...)
        ImageRepository.create_image(payload)
        url = StorageService.generate_presigned_url(s3_key)
```

**Benefits:**
- Hides complexity from API routes
- Reusable across multiple endpoints
- Easier to test and maintain
- Clear separation of concerns

---

### 3. **Dependency Injection / Static Methods**
**Purpose:** Manage dependencies without tightly coupling components

**Implementation:**
```python
# Instead of: self.storage = StorageService()
# We use: StorageService.upload_image(...)  # Stateless, testable
```

**Benefits:**
- Works well with stateless architectures (Lambda, ECS)
- No instance state to manage
- Easy to test with mocks
- Aligns with functional programming principles

---

### 4. **Exception Hierarchy Pattern**
**Purpose:** Granular error handling with custom business exceptions

**Implementation:** `app/core/exception.py`
```python
class ImageNotFoundException(Exception): pass
class ImageUploadException(Exception): pass
class StorageServiceException(Exception): pass
class DatabaseException(Exception): pass
```

**Benefits:**
- Different HTTP status codes for different errors
- Specific error handling per exception type
- Structured error logging with context
- Client-friendly error messages

---

### 5. **Decorator Pattern**
**Purpose:** Add cross-cutting concerns without modifying core logic

**Implementation:** `app/utils/helpers.py`
```python
class Helpers:
    def timer_method(self, func):
        """Measures execution time and logs performance metrics"""
        # Wrapped around async and sync functions
```

**Use Cases:**
- Performance monitoring
- Request/response logging
- Cache management
- Authentication/authorization

---

### 6. **Middleware Pattern**
**Purpose:** Process requests and responses at application level

**Implementation:** `app/main.py - LoggingMiddleware`
```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate/extract request ID
        set_request_id(request_id)
        # Log request
        response = await call_next(request)
        # Log response with status
        return response
```

**Benefits:**
- Centralized request/response logging
- Request ID propagation for tracing
- Transparent to route handlers
- Easy to add new middleware

---

### 7. **Factory/Configuration Pattern**
**Purpose:** Centralized configuration management

**Implementation:** `app/core/config.py`
```python
class Settings(BaseSettings):
    S3_BUCKET_NAME: str
    DYNAMODB_TABLE_NAME: str
    AWS_REGION: str
```

**Benefits:**
- Environment-based configuration
- Type-safe settings
- Easy to switch environments (dev/prod)
- Secrets management ready

---

### 8. **Async/Await Pattern**
**Purpose:** Non-blocking I/O for improved concurrency

**Implementation:**
```python
@router.post("")
async def upload_image(...):
    response = await ImageService.upload_image(file, metadata)
```

**Benefits:**
- Handles more concurrent requests with same resources
- Better performance for I/O-bound operations
- Natural with FastAPI and modern Python

---

## Best Practices Implemented

### 1. **Structured Logging with Context**
**File:** `app/core/logging.py`

```python
# JSON structured logging for machine parsing
logger.info("repository.create_image.start", extra={
    "image_id": metadata.get("image_id"),
    "user_id": metadata.get("user_id")
})

# Includes request ID context for tracing
REQUEST_ID_CTX: ContextVar[Optional[str]] = ContextVar("request_id")
```

**Benefits:**
- Centralized log aggregation (CloudWatch, ELK, Datadog)
- Request tracing across services
- Performance monitoring
- Debugging production issues

**Trade-offs:**
- Slightly more verbose code
- Minimal performance overhead

---

### 2. **Layered Error Handling**
**Location:** `app/main.py`, `app/core/exception.py`

```python
# Custom exceptions logged at creation
@app.exception_handler(ImageNotFoundException)
async def image_not_found_handler(request, exc):
    logger.error("image_not_found_exception", extra={"path": str(request.url.path), "error": str(exc)})
    return create_error_response(404, str(exc))
```

**Benefits:**
- Proper HTTP status codes
- Structured error responses
- Automatic exception logging
- No unhandled exceptions reaching users

---

### 3. **Input Validation (Pydantic)**
**Location:** `app/schemas/image.py`

```python
class ImageUploadSchema(BaseModel):
    user_id: str
    title: str
    tags: List[str]
    
    # Automatic validation and error messages
```

**Benefits:**
- Automatic type checking
- Descriptive validation errors
- OpenAPI documentation generation
- Prevents invalid data propagation

---

### 4. **Presigned URLs for Secure Access**
**Location:** `app/services/storage_service.py`

```python
def generate_presigned_url(key: str):
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=3600,  # 1-hour expiration
    )
```

**Benefits:**
- Offloads large file transfers from backend
- Secure time-limited access
- Reduced backend bandwidth costs
- Improves scalability

**Trade-offs:**
- Client needs to handle S3 directly
- Additional latency if client is geographically distant

---

### 5. **Async/Await for I/O Operations**
**Location:** All service layers

```python
@staticmethod
async def upload_image(file, content_type: str):
    # Non-blocking S3 upload
    s3_client.upload_fileobj(...)
```

**Benefits:**
- Better resource utilization
- Higher throughput under load
- Natural in Python 3.7+

---

### 6. **DynamoDB Query Optimization**
**Location:** `app/repositories/image_repository.py`

```python
# Server-side filtering with FilterExpression
if user_id:
    filter_expression = Attr("user_id").eq(user_id)
response = image_table.scan(FilterExpression=filter_expression)
```

**Benefits:**
- Reduces network traffic
- Filters before returning results
- Leverages DynamoDB's capabilities

**Trade-offs:**
- Scan is less efficient than query (no GSI)
- DynamoDB charges per scanned item, not returned items

---

### 7. **Type Hints Throughout**
**Benefits:**
- Self-documenting code
- IDE autocompletion
- Static type checking with mypy
- Easier maintenance

---

### 8. **Environment-Based Configuration**
**File:** `app/core/config.py`

```python
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
```

**Benefits:**
- Same codebase for dev/staging/prod
- Secrets not hardcoded
- Pydantic handles type conversion
- Secure credential management

---

### 9. **Comprehensive Test Coverage**
**Location:** `tests/test_api.py`

```python
# Mocked AWS resources
@pytest.fixture
def aws_resources(aws_credentials):
    with mock_aws():
        # Create mock S3 and DynamoDB
```

**Benefits:**
- Tests run locally without AWS account
- Fast test execution
- No environmental dependencies
- CI/CD friendly

---

### 10. **Request ID Tracing**
**Implementation:** `app/core/logging.py` + `app/main.py`

```python
# Extract or generate request ID
request_id = request.headers.get("X-Request-ID") or str(uuid4())
set_request_id(request_id)

# Automatically included in all logs
```

**Benefits:**
- Trace requests across logs
- Correlate errors with user actions
- Distributed tracing ready
- Essential for debugging production

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI | Modern, fast, async-ready |
| **ASGI Server** | Uvicorn | High-performance HTTP server |
| **Database** | DynamoDB | Scalable NoSQL for metadata |
| **Storage** | S3 | Scalable object storage |
| **Configuration** | Pydantic Settings | Type-safe config management |
| **AWS SDK** | boto3 | AWS service integration |
| **Testing** | pytest + moto | Unit/integration testing |
| **Logging** | python-json-logger | Structured JSON logging |
| **Deployment** | Docker + Lambda/ECS | Container & serverless |
| **IaC** | Serverless Framework | Infrastructure as code |

---

## API Design

### Endpoints

#### 1. **POST /images** - Upload Image
```
Request:
  - multipart/form-data: file, user_id, title, description, tags
  
Response (200):
  {
    "image_id": "uuid-123",
    "image_url": "https://s3.amazonaws.com/bucket/..."
  }
  
Errors:
  - 400: Invalid image format
  - 422: Validation error
  - 500: Upload failed
```

#### 2. **GET /images** - List Images
```
Request:
  - Query: ?user_id=user1&tag=travel
  
Response (200):
  [
    {
      "image_id": "uuid-123",
      "user_id": "user1",
      "title": "Beach Day",
      "tags": ["travel", "beach"],
      "created_at": "2026-06-02T10:30:00Z"
    }
  ]
```

#### 3. **GET /images/{image_id}** - Get Image Details
```
Response (200):
  {
    "image_id": "uuid-123",
    "title": "Beach Day",
    "download_url": "https://s3.amazonaws.com/bucket/images/uuid-123?..."
  }

Errors:
  - 404: Image not found
```

#### 4. **DELETE /images/{image_id}** - Delete Image
```
Response (200):
  {"message": "Image deleted successfully"}

Errors:
  - 404: Image not found
  - 500: Deletion failed
```

#### 5. **GET /images/get_upload_url** - Get Presigned Upload URL
```
Response (200):
  {
    "image_id": "uuid-123",
    "key": "images/uuid-123",
    "upload_url": "https://s3.amazonaws.com/bucket/images/uuid-123?X-Amz-Algorithm=..."
  }
```

---

## Key Implementation Details

### Request Flow: Upload Image

```
1. Client uploads file to POST /images
   ↓
2. LoggingMiddleware: Extract request ID, log incoming request
   ↓
3. FastAPI route handler: Validate inputs with Pydantic
   ↓
4. ImageService.upload_image():
   a. Validate file format (image/*)
   b. Call StorageService.upload_image() → S3
   c. Prepare metadata payload
   d. Call ImageRepository.create_image() → DynamoDB
   e. Generate presigned GET URL
   ↓
5. Return response with image_id and image_url
   ↓
6. LoggingMiddleware: Log response status and duration
   ↓
7. Structured logs sent to CloudWatch
```

### Request Context Propagation

```
LoggingMiddleware (Generate/Extract request_id)
    ↓
set_request_id(request_id)  # ContextVar
    ↓
RequestContextFilter automatically adds to all logs
    ↓
All logs include: request_id, service_name, timestamp
    ↓
Easy distributed tracing
```

### Error Handling Flow

```
Exception raised in service/repository
    ↓
Caught and logged with context (image_id, user_id, etc.)
    ↓
Re-raised as custom exception (ImageNotFoundException, etc.)
    ↓
Route handler catches and logs again
    ↓
Exception handler in main.py converts to HTTP response
    ↓
Appropriate status code + error message returned
    ↓
Structured error log includes full context
```

---

## Enhancements & Trade-offs

### Enhancement 1: **Add Query Secondary Index (GSI) to DynamoDB**

**Current State:**
```python
# Scans entire table
response = image_table.scan(FilterExpression=Attr("user_id").eq(user_id))
```

**Enhancement:**
```python
# Use GSI for efficient querying
response = image_table.query(
    IndexName="user_id-created_at-index",
    KeyConditionExpression=Key("user_id").eq(user_id)
)
```

**Benefits:**
- Faster queries (O(1) instead of O(n))
- Consistent performance as data grows
- Reduced DynamoDB RCU consumption
- Better pagination support

**Trade-offs:**
- Additional storage for index (10-30% overhead)
- Slightly higher write latency (microseconds)
- Extra cost for index maintenance
- Migration complexity for existing data

**Recommendation:** Implement for production (minimal cost vs. performance gain)

---

### Enhancement 2: **Add Caching Layer (Redis/ElastiCache)**

**Current State:**
- Every request hits DynamoDB

**Enhancement:**
```python
@cache_decorator(ttl=3600)
def get_image(image_id: str):
    return ImageRepository.get_image(image_id)
```

**Benefits:**
- Reduced DynamoDB queries
- Faster response times (sub-millisecond)
- Reduced AWS costs significantly
- Better user experience

**Trade-offs:**
- Additional infrastructure to manage
- Cache invalidation complexity
- Stale data scenarios
- Extra cost for Redis/ElastiCache

**Recommendation:** Add for high-traffic scenarios (80/20 rule: 80% of requests hit 20% of data)

---

### Enhancement 3: **Add Image Processing Pipeline**

**Current State:**
- No image transformation

**Enhancement:**
```python
async def upload_image(file, metadata):
    # Upload original
    await StorageService.upload_image(file, ...)
    
    # Create thumbnails asynchronously
    await create_thumbnail(image_id, sizes=[150, 300, 600])
    
    # Extract metadata (EXIF, dimensions, etc.)
    metadata = extract_image_metadata(file)
```

**Benefits:**
- Better UX with thumbnails
- Search by image properties
- CDN optimization
- Progressive loading

**Trade-offs:**
- Asynchronous job queues needed (SQS)
- Additional storage (3-4x for thumbnails)
- Lambda/compute time increased
- Complexity of job management

**Recommendation:** Use async jobs (SQS + Lambda) for production

---

### Enhancement 4: **Add Rate Limiting & Quota Management**

**Current State:**
- No rate limiting

**Enhancement:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.get("/images")
@limiter.limit("100/minute")
async def list_images(...):
    pass
```

**Benefits:**
- Prevents API abuse
- Fair resource sharing
- Protects backend
- Predictable costs

**Trade-offs:**
- Additional complexity
- False positives (shared IPs)
- Needs persistent state (Redis)
- User experience impact

**Recommendation:** Implement at API Gateway level (no code cost)

---

### Enhancement 5: **Add Audit Logging**

**Current State:**
- Operational logs only

**Enhancement:**
```python
# Track who did what and when
audit_log = {
    "action": "DELETE_IMAGE",
    "user_id": user_id,
    "image_id": image_id,
    "timestamp": now(),
    "status": "SUCCESS",
    "ip_address": request.client.host
}
AuditRepository.log(audit_log)
```

**Benefits:**
- Compliance requirements (GDPR, SOC2)
- Security investigations
- Usage analytics
- Accountability

**Trade-offs:**
- Additional storage
- Separate audit table/index
- Query performance impact
- Privacy considerations

**Recommendation:** Implement for regulated environments

---

### Enhancement 6: **Add Image Versioning**

**Current State:**
- Overwrites on update

**Enhancement:**
```python
# Store versions in metadata
metadata = {
    "image_id": image_id,
    "version": 1,
    "versions": [
        {"version": 1, "s3_key": "...", "created_at": "..."},
        {"version": 2, "s3_key": "...", "created_at": "..."}
    ]
}
```

**Benefits:**
- Recover from accidental deletes
- Compare historical versions
- Rollback capability

**Trade-offs:**
- Storage multiplied by version count
- Metadata query complexity
- DynamoDB item size limits (400KB)
- Implementation complexity

**Recommendation:** Implement only if needed for use case

---

### Enhancement 7: **Add Search Capabilities**

**Current State:**
- Only filter by user_id and tag

**Enhancement:**
```python
# Integration with Elasticsearch
search_results = elasticsearch.search(
    index="images",
    query={
        "multi_match": {
            "query": "beach sunset",
            "fields": ["title", "description", "tags"]
        }
    }
)
```

**Benefits:**
- Full-text search
- Fuzzy matching
- Relevance scoring
- Better UX

**Trade-offs:**
- Additional service to operate
- Sync complexity between DynamoDB and ES
- Cost (ES cluster)
- Operational overhead

**Recommendation:** Defer until needed (not MVP requirement)

---

### Enhancement 8: **Add Batch Operations**

**Current State:**
- Single image operations only

**Enhancement:**
```python
@router.post("/images/batch")
async def batch_upload(files: List[UploadFile]):
    # Use DynamoDB batch_write_item
    # Parallel S3 uploads
    pass

@router.delete("/images/batch")
async def batch_delete(image_ids: List[str]):
    # Efficient batch delete
    pass
```

**Benefits:**
- Better performance for bulk ops
- Reduced API calls
- More efficient DynamoDB operations

**Trade-offs:**
- Added complexity
- Request size limits
- Error handling complexity

**Recommendation:** Add if bulk operations are common

---

### Enhancement 9: **Add Soft Deletes**

**Current State:**
- Hard delete only

**Enhancement:**
```python
def soft_delete(image_id: str):
    # Update: deleted_at = now()
    # Don't actually delete
    repository.update_image(image_id, {"deleted_at": now()})

def list_images(...):
    # Filter: deleted_at IS NULL
```

**Benefits:**
- Recover deleted images
- Audit trail
- GDPR right to be forgotten (with scheduled deletion)

**Trade-offs:**
- Additional complexity
- Query filtering overhead
- Storage never freed

**Recommendation:** Implement with scheduled hard delete

---

### Enhancement 10: **Add WebSocket Support for Real-time Updates**

**Current State:**
- REST polling only

**Enhancement:**
```python
@app.websocket("/ws/images/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # Notify on new uploads
    # Real-time deletions
    # Live notifications
```

**Benefits:**
- Real-time experience
- Reduced polling overhead
- Better UX

**Trade-offs:**
- Connection state management
- Increased infrastructure complexity
- Scaling challenges
- Additional latency (connection overhead)

**Recommendation:** Implement if real-time is core requirement

---

## Interview Talking Points

### 1. **Scalability Architecture**
- **Stateless design**: Easy horizontal scaling (Lambda, ECS)
- **S3 presigned URLs**: Offload large transfers, avoid bottleneck
- **Async/await**: Handle concurrent requests efficiently
- **DynamoDB**: Auto-scales with demand, pay-per-request

### 2. **Separation of Concerns**
- API layer (HTTP)
- Service layer (business logic)
- Repository layer (data access)
- Infrastructure (AWS services)
- Cross-cutting (logging, error handling)

### 3. **Error Handling Strategy**
- Custom exception hierarchy
- Structured error logging
- Appropriate HTTP status codes
- Request context for debugging

### 4. **Observability**
- Structured JSON logging
- Request ID tracing
- Performance metrics (timing decorator)
- Comprehensive log context

### 5. **Testing Approach**
- Mocked AWS services (moto)
- Local test execution
- No external dependencies
- Fast feedback loop

### 6. **Security Considerations**
- Presigned URLs (time-limited)
- IAM roles for Lambda
- Environment-based secrets
- Input validation (Pydantic)

### 7. **Cost Optimization**
- Presigned URLs reduce bandwidth
- DynamoDB on-demand pricing
- No always-on infrastructure (Lambda)
- Efficient queries with GSI

### 8. **Production Readiness**
- Docker containerization
- Environment configuration
- Error handling and logging
- CI/CD ready (tests, linting)
- Infrastructure as code (Serverless)

### 9. **Design Decisions & Trade-offs**
- Why DynamoDB vs. PostgreSQL?
  - Scalability, managed service, pay-per-request
- Why S3 presigned URLs?
  - Reduce backend load, improve scalability
- Why Repository pattern?
  - Testability, flexibility, clean code
- Why structured logging?
  - Observability, debugging, compliance

### 10. **Potential Improvements**
- GSI for efficient user queries
- Caching layer for hot data
- Image processing pipeline
- Rate limiting at API Gateway
- Elasticsearch for search
- Soft deletes for recovery

---

## Summary: Key Takeaways for Interview

| Aspect | Implementation | Why It Matters |
|--------|----------------|----------------|
| **Architecture** | Layered + Microservices ready | Scalable, maintainable, testable |
| **Design Patterns** | Repository, Service, Middleware | SOLID principles, flexibility |
| **Error Handling** | Custom exceptions, structured logs | Production-grade observability |
| **Async/Await** | Throughout request flow | Better performance, scalability |
| **Testing** | Moto mocks, local execution | Fast, reliable, no dependencies |
| **Configuration** | Pydantic Settings, .env | Easy environment management |
| **API Design** | RESTful, presigned URLs | Secure, scalable, user-friendly |
| **Logging** | JSON structured, request IDs | Distributed tracing, debugging |
| **Deployment** | Docker, Lambda/ECS ready | Flexible, production-ready |
| **Security** | IAM roles, time-limited URLs | Least privilege, secure access |

---

## Conversation Starters

1. "Can you walk me through the upload flow?"
   → Show layered architecture, async handling, error handling

2. "Why DynamoDB and not a relational database?"
   → Scalability, managed service, pay-per-request, serverless-friendly

3. "How do you ensure data consistency?"
   → Transactions (if needed), error handling, retry logic, strong consistent reads

4. "What would you change with 10x traffic?"
   → GSI for queries, caching, image processing queue, CDN for thumbnails

5. "How do you debug production issues?"
   → Structured logging, request ID tracing, CloudWatch dashboards, distributed tracing

6. "What's the most challenging part?"
   → Distributed testing, eventual consistency, async error handling, cost optimization

7. "How would you add real-time notifications?"
   → WebSockets, SNS/SQS, event-driven architecture, pub-sub pattern

8. "Tell me about testing strategy?"
   → Moto for AWS mocking, pytest-asyncio, fixtures, local execution, CI/CD

---

## Deployment & Operations

### Local Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/
```

### Docker
```bash
docker build -f deployment/docker/Dockerfile -t image-service:latest .
docker run -e AWS_REGION=ap-south-1 image-service:latest
```

### AWS Lambda
```bash
serverless deploy --stage prod
# Automatically creates API Gateway, Lambda, IAM roles
```

### Environment Configuration
```bash
# .env file
AWS_REGION=ap-south-1
S3_BUCKET_NAME=image-service-bucket
DYNAMODB_TABLE_NAME=image-service-table
LOG_LEVEL=INFO
```

---

**Good luck with your interview! Focus on explaining the "why" behind each design decision.**
