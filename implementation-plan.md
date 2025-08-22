# AI Sales Assistant - Detailed Implementation Plan

## Executive Summary

This document outlines the complete technical implementation plan for the AI Sales Assistant MVP, leveraging the latest OpenAI GPT-5, Vector Stores, and Assistants API capabilities released in August 2025.

## System Architecture Overview

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Chrome         │    │  FastAPI        │    │  OpenAI         │
│  Extension      │────│  Backend        │────│  Services       │
│  (Frontend)     │    │  (Orchestrator) │    │  (AI Engine)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────│  WebSocket      │─────────────┘
                        │  Connection     │
                        └─────────────────┘
```

### Core Components

#### 1. Chrome Extension (Frontend)
- **Technology**: Manifest V3, React 18, TypeScript
- **Responsibilities**:
  - Audio capture via Chrome Tab Capture API
  - Real-time UI overlay for suggestions
  - WebSocket communication with backend
  - Knowledge base file uploads
  - User authentication and settings

#### 2. FastAPI Backend (Orchestrator)
- **Technology**: Python 3.11+, FastAPI, WebSockets, Redis
- **Responsibilities**:
  - WebSocket connection management
  - Audio stream processing coordination
  - OpenAI API integration
  - User session management
  - Real-time suggestion delivery

#### 3. OpenAI AI Engine
- **GPT-5 Integration**: Latest model with reasoning capabilities
- **Vector Store**: Knowledge base storage and retrieval
- **Assistants API**: Conversation context and tool calling
- **Whisper**: Real-time speech-to-text processing

## Detailed Component Design

### 1. Audio Capture & Processing Layer

#### Chrome Extension Audio Capture
```typescript
// Audio capture using Chrome Tab Capture API
interface AudioCaptureService {
  startCapture(): Promise<MediaStream>
  stopCapture(): void
  getAudioStream(): MediaStream
}

// Real-time audio streaming to backend
interface AudioStreamManager {
  connect(): Promise<WebSocket>
  sendAudioChunk(audioData: ArrayBuffer): void
  onSuggestion(callback: (suggestion: Suggestion) => void): void
}
```

#### Backend Audio Processing
```python
# FastAPI WebSocket handler for audio streams
class AudioStreamHandler:
    async def handle_audio_stream(self, websocket: WebSocket)
    async def process_audio_chunk(self, audio_data: bytes) -> str
    async def transcribe_with_whisper(self, audio_data: bytes) -> TranscriptionResult
```

### 2. Speech Processing Engine

#### Real-Time Transcription
- **Technology**: OpenAI Whisper API
- **Features**: 
  - Speaker identification
  - Conversation flow tracking
  - Sub-300ms latency target
  - Continuous transcription buffer

```python
# Whisper integration with streaming
class SpeechProcessor:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.transcription_buffer = []
    
    async def transcribe_stream(self, audio_chunk: bytes) -> TranscriptionResult:
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_chunk,
            response_format="json",
            timestamp_granularities=["word"]
        )
        return response
```

### 3. Intelligence Engine (GPT-5 + Assistants)

#### GPT-5 Integration
```python
# GPT-5 with latest capabilities
class IntelligenceEngine:
    def __init__(self):
        self.client = OpenAI()
        self.assistant_id = None
        self.vector_store_id = None
    
    async def analyze_conversation(self, 
                                 conversation_context: str,
                                 user_query: str) -> List[Suggestion]:
        response = await self.client.responses.create(
            model="gpt-5",
            reasoning_effort="medium",  # New GPT-5 parameter
            verbosity="medium",         # New GPT-5 parameter
            input=[{
                "role": "user", 
                "content": self._build_analysis_prompt(conversation_context, user_query)
            }],
            tools=[{
                "type": "file_search",
                "file_search": {
                    "vector_store_ids": [self.vector_store_id]
                }
            }]
        )
        return self._parse_suggestions(response)
```

#### OpenAI Assistants API Integration
```python
# Assistants API for conversation context
class ConversationAssistant:
    async def create_assistant(self, vector_store_id: str) -> str:
        assistant = await self.client.beta.assistants.create(
            name="Sales Assistant",
            instructions="""You are an expert sales assistant that provides 
                          real-time suggestions during sales conversations.""",
            model="gpt-5",
            tools=[{
                "type": "file_search",
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }]
        )
        return assistant.id
    
    async def create_thread(self) -> str:
        thread = await self.client.beta.threads.create()
        return thread.id
    
    async def get_suggestion(self, thread_id: str, message: str) -> List[str]:
        # Add message to thread
        await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Stream response with new streaming capabilities
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        ) as stream:
            suggestions = []
            for event in stream:
                if event.event == "thread.message.delta":
                    suggestions.append(event.data.delta.content)
            return suggestions
```

### 4. Knowledge Management System (Vector Store)

#### Vector Store Setup
```python
# Vector Store integration with latest API
class KnowledgeManager:
    async def create_vector_store(self, name: str) -> str:
        vector_store = await self.client.vector_stores.create(
            name=name,
            metadata={"purpose": "sales_knowledge_base"}
        )
        return vector_store.id
    
    async def upload_documents(self, vector_store_id: str, files: List[bytes]) -> None:
        # Batch upload with new file batch API
        file_batch = await self.client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=files
        )
        return file_batch
    
    async def search_knowledge(self, vector_store_id: str, query: str) -> List[str]:
        search_results = await self.client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            limit=5
        )
        return [result.content for result in search_results.data]
```

### 5. Real-Time Suggestion Engine

#### Trigger Detection System
```python
class TriggerDetector:
    def __init__(self):
        self.question_patterns = [
            r"how does.*\?",
            r"what about.*\?",
            r"can you.*\?",
            r"do you have.*\?",
            r"tell me about.*\?"
        ]
        self.objection_patterns = [
            r"that's expensive",
            r"we're already using",
            r"i'm not sure",
            r"we need to think about it",
            r"compared to.*"
        ]
    
    def detect_triggers(self, transcript: str) -> List[TriggerType]:
        triggers = []
        
        # Question detection
        for pattern in self.question_patterns:
            if re.search(pattern, transcript.lower()):
                triggers.append(TriggerType.QUESTION)
        
        # Objection detection
        for pattern in self.objection_patterns:
            if re.search(pattern, transcript.lower()):
                triggers.append(TriggerType.OBJECTION)
        
        # Pause detection (3+ seconds of silence)
        if self._detect_pause(transcript):
            triggers.append(TriggerType.PAUSE)
        
        return triggers
```

#### Suggestion Generation
```python
class SuggestionGenerator:
    async def generate_suggestions(self, 
                                 context: ConversationContext,
                                 trigger_type: TriggerType) -> List[Suggestion]:
        
        prompt = self._build_suggestion_prompt(context, trigger_type)
        
        # Use GPT-5 with custom tools for better formatting
        response = await self.client.responses.create(
            model="gpt-5",
            reasoning_effort="low",  # Fast suggestions
            verbosity="low",         # Concise responses
            input=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "custom",
                "custom": {
                    "name": "format_suggestions",
                    "description": "Format sales suggestions",
                    "parameters": {
                        "type": "string",
                        "format": "suggestion1|suggestion2|suggestion3"
                    }
                }
            }]
        )
        
        return self._parse_suggestions(response)
```

## User Interface Design

### Chrome Extension UI Components

#### Main Overlay Component
```typescript
interface SalesAssistantOverlay {
  status: 'listening' | 'processing' | 'suggestions' | 'idle'
  suggestions: Suggestion[]
  isMinimized: boolean
}

interface Suggestion {
  id: string
  text: string
  confidence: number
  category: 'question' | 'objection' | 'technical' | 'pricing'
  actionButtons: ActionButton[]
}

interface ActionButton {
  type: 'copy' | 'more_info' | 'customize'
  action: () => void
}
```

#### React Components Structure
```typescript
// Main overlay component
const SalesAssistantOverlay: React.FC = () => {
  const [status, setStatus] = useState<AssistantStatus>('idle')
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [isConnected, setIsConnected] = useState(false)
  
  // WebSocket connection for real-time suggestions
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'suggestion') {
        setSuggestions(data.suggestions)
      }
    }
  }, [])
  
  return (
    <div className="sales-assistant-overlay">
      <StatusBar status={status} />
      <SuggestionList suggestions={suggestions} />
      <ControlPanel />
    </div>
  )
}
```

## Development Phases

### Phase 1: Core MVP (Months 1-3)
**Objective**: Basic real-time suggestions during meetings

**Features**:
- Chrome extension with audio capture
- Basic speech-to-text processing
- Simple AI suggestions using GPT-5
- Basic knowledge base upload
- One-click copy functionality

**Technical Deliverables**:
- Chrome extension (Manifest V3)
- FastAPI backend with WebSocket support
- GPT-5 integration for suggestion generation
- Vector store for knowledge base
- Basic UI overlay

### Phase 2: Enhanced Intelligence (Months 4-6)
**Objective**: Advanced AI capabilities and user experience

**Features**:
- Advanced trigger detection (questions, objections, pauses)
- Context-aware suggestions with conversation history
- Improved knowledge base management
- User feedback and learning system
- Analytics dashboard

**Technical Deliverables**:
- OpenAI Assistants API integration
- Advanced trigger detection algorithms
- Conversation context management
- User feedback collection system
- Performance analytics

### Phase 3: Scale & Enterprise (Months 7-12)
**Objective**: Enterprise features and scalability

**Features**:
- Team knowledge sharing
- CRM integrations (Salesforce, HubSpot)
- Advanced analytics and reporting
- Enterprise security features
- Multi-platform support (Firefox, Safari)

**Technical Deliverables**:
- Multi-tenant architecture
- CRM API integrations
- Advanced security implementation
- Scalable infrastructure
- Enterprise admin dashboard

## Technology Stack Details

### Frontend (Chrome Extension)
```json
{
  "manifest_version": 3,
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "zustand": "^4.4.0",
    "socket.io-client": "^4.7.0"
  },
  "permissions": [
    "tabCapture",
    "activeTab",
    "storage",
    "scripting"
  ]
}
```

### Backend (FastAPI)
```python
# requirements.txt
fastapi==0.104.0
uvicorn==0.24.0
websockets==12.0
redis==5.0.0
openai==1.68.0  # Latest version with GPT-5 support
python-multipart==0.0.6
pydantic==2.5.0
```

### OpenAI Services Integration
```python
# OpenAI client configuration
class OpenAIConfig:
    API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_GPT5 = "gpt-5"
    MODEL_GPT5_MINI = "gpt-5-mini"
    WHISPER_MODEL = "whisper-1"
    
    # GPT-5 specific parameters
    REASONING_EFFORT = "medium"
    VERBOSITY = "low"
    MAX_TOKENS = 128000
    
    # Vector store configuration
    VECTOR_STORE_NAME = "sales_knowledge_base"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
```

## API Integration Patterns

### 1. Real-Time Audio Processing
```python
class AudioProcessor:
    async def setup_audio_pipeline(self):
        # WebSocket for audio streaming
        self.audio_ws = await websockets.connect("ws://localhost:8000/audio")
        
        # Whisper transcription
        self.whisper_client = OpenAI()
        
        # GPT-5 for analysis
        self.gpt5_client = OpenAI()
    
    async def process_audio_stream(self, audio_chunk: bytes):
        # 1. Transcribe with Whisper
        transcription = await self.whisper_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_chunk,
            response_format="json"
        )
        
        # 2. Detect triggers
        triggers = self.trigger_detector.detect(transcription.text)
        
        # 3. Generate suggestions if triggered
        if triggers:
            suggestions = await self.generate_suggestions(
                transcription.text, 
                triggers
            )
            return suggestions
```

### 2. Vector Store Knowledge Management
```python
class KnowledgeBaseManager:
    async def initialize_knowledge_base(self, user_id: str):
        # Create user-specific vector store
        vector_store = await self.client.vector_stores.create(
            name=f"sales_kb_{user_id}",
            metadata={"user_id": user_id, "created_at": datetime.utcnow().isoformat()}
        )
        
        return vector_store.id
    
    async def upload_documents(self, vector_store_id: str, files: List[UploadFile]):
        # Batch upload with new Vector Store Files API
        file_batch = await self.client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=[file.file for file in files]
        )
        
        # Wait for processing
        while file_batch.status == "in_progress":
            await asyncio.sleep(1)
            file_batch = await self.client.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store_id,
                batch_id=file_batch.id
            )
        
        return file_batch
    
    async def search_knowledge(self, vector_store_id: str, query: str) -> List[str]:
        # Use new Vector Store search capability
        search_results = await self.client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            limit=5
        )
        
        return [result.content for result in search_results.data]
```

### 3. Assistants API for Context Management
```python
class ConversationManager:
    async def create_sales_assistant(self, vector_store_id: str):
        # Create assistant with file search tool
        assistant = await self.client.beta.assistants.create(
            name="Sales Conversation Assistant",
            instructions="""You are an expert sales assistant. Analyze conversation 
                          context and provide 2-3 relevant, actionable suggestions 
                          based on the company's knowledge base. Focus on:
                          1. Answering customer questions accurately
                          2. Handling objections with data and benefits
                          3. Moving conversations toward next steps
                          Keep suggestions concise and natural.""",
            model="gpt-5",
            tools=[{
                "type": "file_search",
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }]
        )
        return assistant.id
    
    async def get_contextual_suggestions(self, 
                                       thread_id: str, 
                                       conversation_snippet: str) -> List[str]:
        # Add conversation to thread
        await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Customer said: '{conversation_snippet}'. Provide 3 helpful response suggestions."
        )
        
        # Stream response for real-time suggestions
        suggestions = []
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        ) as stream:
            for event in stream:
                if event.event == "thread.message.delta" and event.data.delta.content:
                    content = event.data.delta.content[0].text.value
                    suggestions.append(content)
        
        return self._parse_numbered_suggestions(suggestions)
```

## Smart Trigger Detection System

### Advanced Pattern Recognition
```python
class AdvancedTriggerDetector:
    def __init__(self):
        # Use GPT-5 for intelligent trigger detection
        self.client = OpenAI()
    
    async def analyze_conversation_flow(self, transcript: str) -> TriggerAnalysis:
        response = await self.client.responses.create(
            model="gpt-5-mini",  # Fast model for real-time analysis
            reasoning_effort="minimal",  # Fastest response
            verbosity="low",
            input=[{
                "role": "user",
                "content": f"""Analyze this sales conversation transcript and identify:
                
                Transcript: "{transcript}"
                
                Identify:
                1. Questions that need answers (true/false)
                2. Objections raised (true/false)  
                3. Technical requests (true/false)
                4. Buying signals (true/false)
                5. Confusion or hesitation (true/false)
                
                Respond with JSON: {{"questions": bool, "objections": bool, "technical": bool, "buying_signals": bool, "confusion": bool}}"""
            }],
            response_format={"type": "json_object"}
        )
        
        return TriggerAnalysis.parse_raw(response.output_text)
```

## Real-Time System Flow

### Complete Audio-to-Suggestion Pipeline
```python
class RealTimePipeline:
    async def process_meeting_audio(self, audio_stream: AsyncIterator[bytes]):
        async for audio_chunk in audio_stream:
            # 1. Transcribe audio (Whisper)
            transcription = await self.speech_processor.transcribe_stream(audio_chunk)
            
            # 2. Update conversation buffer
            self.conversation_buffer.append(transcription.text)
            
            # 3. Detect triggers (GPT-5 mini)
            triggers = await self.trigger_detector.analyze_conversation_flow(
                " ".join(self.conversation_buffer[-10:])  # Last 10 statements
            )
            
            # 4. Generate suggestions if triggered (GPT-5 + Assistant)
            if any(triggers.__dict__.values()):
                suggestions = await self.suggestion_generator.get_contextual_suggestions(
                    thread_id=self.thread_id,
                    conversation_snippet=transcription.text
                )
                
                # 5. Send to frontend via WebSocket
                await self.websocket.send_json({
                    "type": "suggestions",
                    "data": suggestions,
                    "timestamp": time.time()
                })
```

## Data Models

### Core Data Structures
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TriggerType(Enum):
    QUESTION = "question"
    OBJECTION = "objection"
    PAUSE = "pause"
    TECHNICAL = "technical"
    BUYING_SIGNAL = "buying_signal"

class Suggestion(BaseModel):
    id: str
    text: str
    confidence: float
    category: str
    source_documents: List[str]
    created_at: datetime

class ConversationContext(BaseModel):
    thread_id: str
    assistant_id: str
    vector_store_id: str
    conversation_history: List[str]
    current_transcript: str
    detected_triggers: List[TriggerType]

class UserSession(BaseModel):
    user_id: str
    session_id: str
    meeting_platform: str
    vector_store_id: str
    assistant_id: str
    thread_id: str
    is_active: bool
    created_at: datetime
```

## Security & Privacy Implementation

### Data Protection
```python
class SecurityManager:
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
    
    def encrypt_audio_data(self, audio: bytes) -> bytes:
        # Encrypt audio before processing
        return self._encrypt(audio)
    
    def anonymize_transcript(self, transcript: str) -> str:
        # Remove PII from transcripts
        return self._remove_pii(transcript)
    
    async def secure_knowledge_upload(self, file: UploadFile, user_id: str):
        # Validate file type and size
        if not self._is_valid_file(file):
            raise ValidationError("Invalid file type")
        
        # Scan for sensitive information
        content = await file.read()
        if self._contains_sensitive_data(content):
            raise SecurityError("File contains sensitive information")
        
        return content
```

### GDPR/CCPA Compliance
```python
class ComplianceManager:
    async def handle_data_deletion_request(self, user_id: str):
        # Delete user's vector store
        await self.client.vector_stores.delete(f"sales_kb_{user_id}")
        
        # Delete assistant
        await self.client.beta.assistants.delete(f"assistant_{user_id}")
        
        # Delete local user data
        await self.db.delete_user_data(user_id)
    
    async def export_user_data(self, user_id: str) -> dict:
        # Export all user data for GDPR requests
        return {
            "knowledge_base": await self._export_vector_store(user_id),
            "conversation_history": await self._export_conversations(user_id),
            "suggestions_used": await self._export_suggestion_history(user_id)
        }
```

## Performance Optimization

### Caching Strategy
```python
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
    
    async def cache_frequent_suggestions(self, query: str, suggestions: List[str]):
        # Cache common suggestions to reduce API calls
        cache_key = f"suggestions:{hashlib.md5(query.encode()).hexdigest()}"
        await self.redis_client.setex(cache_key, 3600, json.dumps(suggestions))
    
    async def get_cached_suggestions(self, query: str) -> Optional[List[str]]:
        cache_key = f"suggestions:{hashlib.md5(query.encode()).hexdigest()}"
        cached = await self.redis_client.get(cache_key)
        return json.loads(cached) if cached else None
```

### Latency Optimization
```python
class LatencyOptimizer:
    async def optimize_suggestion_pipeline(self):
        # Use GPT-5 mini for real-time triggers
        # Use GPT-5 for complex suggestions
        # Implement suggestion pre-loading for common scenarios
        
        # Pre-load common responses
        await self._preload_common_suggestions()
        
        # Use connection pooling for OpenAI API
        self.openai_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5),
            connector=aiohttp.TCPConnector(limit=100)
        )
```

## Testing Strategy

### Unit Testing
```python
# Test suggestion generation
async def test_suggestion_generation():
    engine = IntelligenceEngine()
    suggestions = await engine.generate_suggestions(
        context="Customer asked about API rate limits",
        trigger_type=TriggerType.QUESTION
    )
    
    assert len(suggestions) >= 2
    assert all(s.confidence > 0.7 for s in suggestions)
    assert any("API" in s.text for s in suggestions)

# Test trigger detection
async def test_trigger_detection():
    detector = TriggerDetector()
    triggers = await detector.detect_triggers(
        "How does your security feature work exactly?"
    )
    
    assert TriggerType.QUESTION in triggers
```

### Integration Testing
```python
# Test complete pipeline
async def test_audio_to_suggestion_pipeline():
    pipeline = RealTimePipeline()
    
    # Mock audio input
    mock_audio = create_mock_audio("How much does this cost?")
    
    # Process through pipeline
    suggestions = await pipeline.process_audio_chunk(mock_audio)
    
    # Verify suggestions relate to pricing
    assert any("pricing" in s.category for s in suggestions)
    assert len(suggestions) <= 3  # UI limit
```

## Deployment Architecture

### Cloud Infrastructure
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Chrome Extension Deployment
```json
{
  "name": "AI Sales Assistant",
  "version": "1.0.0",
  "manifest_version": 3,
  "permissions": [
    "tabCapture",
    "activeTab", 
    "storage"
  ],
  "host_permissions": [
    "https://meet.google.com/*",
    "https://zoom.us/*",
    "https://*.teams.microsoft.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": [
      "https://meet.google.com/*",
      "https://zoom.us/*", 
      "https://*.teams.microsoft.com/*"
    ],
    "js": ["content.js"]
  }]
}
```

## Monitoring & Analytics

### Performance Metrics
```python
class MetricsCollector:
    async def track_suggestion_metrics(self, suggestion: Suggestion, user_action: str):
        # Track suggestion effectiveness
        metrics = {
            "suggestion_id": suggestion.id,
            "user_action": user_action,  # copied, ignored, customized
            "confidence": suggestion.confidence,
            "category": suggestion.category,
            "timestamp": time.time()
        }
        
        await self.analytics_db.insert_metric(metrics)
    
    async def track_performance_metrics(self):
        # Track system performance
        return {
            "average_latency": await self._calculate_avg_latency(),
            "suggestion_acceptance_rate": await self._calculate_acceptance_rate(),
            "api_usage": await self._get_openai_usage(),
            "error_rate": await self._calculate_error_rate()
        }
```

## Cost Management

### OpenAI API Cost Optimization
```python
class CostOptimizer:
    def __init__(self):
        # GPT-5 pricing: $1.25/1M input, $10/1M output
        # GPT-5 mini: $0.25/1M input, $2/1M output
        # Whisper: $0.006/minute
        
        self.gpt5_input_cost = 1.25 / 1_000_000
        self.gpt5_output_cost = 10 / 1_000_000
        self.gpt5_mini_input_cost = 0.25 / 1_000_000
        self.gpt5_mini_output_cost = 2 / 1_000_000
        self.whisper_cost = 0.006 / 60  # per second
    
    async def estimate_session_cost(self, duration_minutes: int) -> float:
        # Estimate costs for a meeting session
        whisper_cost = duration_minutes * self.whisper_cost * 60
        
        # Estimate GPT-5 usage (avg 10 suggestions per hour)
        suggestions_count = (duration_minutes / 60) * 10
        gpt5_cost = suggestions_count * (
            (500 * self.gpt5_input_cost) +  # 500 tokens input avg
            (150 * self.gpt5_output_cost)   # 150 tokens output avg
        )
        
        return whisper_cost + gpt5_cost
    
    def select_optimal_model(self, complexity_score: float) -> str:
        # Use GPT-5 mini for simple triggers, GPT-5 for complex
        if complexity_score < 0.5:
            return "gpt-5-mini"
        else:
            return "gpt-5"
```

## Business Logic Implementation

### Subscription Management
```python
class SubscriptionManager:
    TIER_LIMITS = {
        "free": {"hours_per_month": 5, "knowledge_uploads": 1},
        "professional": {"hours_per_month": 50, "knowledge_uploads": None},
        "team": {"hours_per_month": None, "knowledge_uploads": None},
        "enterprise": {"hours_per_month": None, "knowledge_uploads": None}
    }
    
    async def check_usage_limits(self, user_id: str, action: str) -> bool:
        user_tier = await self.get_user_tier(user_id)
        current_usage = await self.get_current_usage(user_id)
        
        limits = self.TIER_LIMITS[user_tier]
        
        if action == "start_meeting":
            if limits["hours_per_month"] is None:
                return True
            return current_usage["hours_used"] < limits["hours_per_month"]
        
        if action == "upload_knowledge":
            if limits["knowledge_uploads"] is None:
                return True
            return current_usage["uploads_count"] < limits["knowledge_uploads"]
        
        return False
```

## Error Handling & Resilience

### Robust Error Management
```python
class ErrorHandler:
    async def handle_openai_api_error(self, error: Exception) -> dict:
        if isinstance(error, openai.RateLimitError):
            return {
                "error": "rate_limit",
                "message": "Too many requests. Please wait a moment.",
                "retry_after": error.retry_after
            }
        
        elif isinstance(error, openai.AuthenticationError):
            return {
                "error": "authentication",
                "message": "API key invalid. Please check configuration."
            }
        
        elif isinstance(error, openai.APIConnectionError):
            return {
                "error": "connection",
                "message": "Unable to connect to OpenAI. Retrying...",
                "action": "retry"
            }
        
        else:
            return {
                "error": "unknown",
                "message": "An unexpected error occurred.",
                "details": str(error)
            }
    
    async def implement_fallback_suggestions(self, context: str) -> List[str]:
        # Provide basic suggestions when AI fails
        return [
            "Let me get back to you with detailed information on that.",
            "I can connect you with our technical team for specifics.",
            "Would you like me to send you our documentation on this topic?"
        ]
```

## Success Metrics & KPIs

### Technical Metrics
```python
class SuccessMetrics:
    TARGET_METRICS = {
        "response_latency": 300,  # ms
        "suggestion_accuracy": 0.85,
        "uptime": 0.99,
        "user_satisfaction": 4.5,
        "suggestion_acceptance_rate": 0.60
    }
    
    async def calculate_success_score(self) -> dict:
        metrics = await self.collect_all_metrics()
        
        return {
            "technical_score": self._calculate_technical_score(metrics),
            "user_experience_score": self._calculate_ux_score(metrics),
            "business_impact_score": self._calculate_business_score(metrics),
            "overall_success": self._calculate_overall_success(metrics)
        }
```

## Risk Mitigation Strategies

### Technical Risk Mitigation
```python
class RiskMitigation:
    async def implement_audio_quality_fallbacks(self):
        # Multiple audio processing strategies
        strategies = [
            self._process_with_noise_reduction,
            self._process_with_echo_cancellation,
            self._process_with_basic_cleanup
        ]
        
        for strategy in strategies:
            try:
                result = await strategy(audio_data)
                if self._is_quality_acceptable(result):
                    return result
            except Exception:
                continue
        
        # Final fallback to manual transcription prompt
        return self._prompt_manual_input()
    
    async def handle_platform_compatibility(self, platform: str):
        # Adaptive strategies for different meeting platforms
        platform_configs = {
            "zoom": {"audio_format": "webm", "capture_method": "tab"},
            "meet": {"audio_format": "mp4", "capture_method": "tab"},
            "teams": {"audio_format": "wav", "capture_method": "desktop"}
        }
        
        return platform_configs.get(platform, platform_configs["zoom"])
```

## Next Steps & Future Enhancements

### Short-term Roadmap (6 months)
1. **Advanced Context Awareness**: Multi-turn conversation memory
2. **Improved Accuracy**: Fine-tuning on sales conversation data
3. **Enhanced UI**: Customizable suggestion styles and preferences
4. **Performance Optimization**: Sub-200ms response times

### Medium-term Roadmap (12 months)  
1. **Multi-platform Support**: Firefox and Safari extensions
2. **CRM Integrations**: Salesforce, HubSpot, Pipedrive APIs
3. **Advanced Analytics**: Conversion tracking, ROI measurement
4. **Team Features**: Shared knowledge bases, team analytics

### Long-term Vision (18+ months)
1. **Mobile Companion**: iOS/Android apps for phone calls
2. **Industry Specialization**: Vertical-specific knowledge bases
3. **Advanced AI Training**: Custom model fine-tuning on user data
4. **International Expansion**: Multi-language support

---

This implementation plan provides a comprehensive roadmap for building the AI Sales Assistant using the latest OpenAI GPT-5 capabilities, ensuring scalability, security, and optimal user experience.