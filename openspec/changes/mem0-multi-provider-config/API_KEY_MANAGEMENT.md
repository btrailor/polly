# API Key Management & Provider Onboarding - Design Proposal

**Date:** February 13, 2026  
**Status:** 📝 Design Exploration  
**Goal:** Elegant, user-friendly API key management for all LiteLLM providers

---

## Problem Statement

### Current State
- API keys stored in environment variables or config files
- No UI for key management
- Unclear where to get keys
- No validation or testing
- No guidance for new providers

### User Pain Points
1. **"Where do I get an API key?"** - No links to provider dashboards
2. **"Is my key working?"** - No validation feedback
3. **"What providers are available?"** - Hidden in documentation
4. **"How much will this cost?"** - No pricing visibility
5. **"Which provider should I use?"** - No recommendations

---

## Design Goals

### Aesthetic Principles
- **Clean & Minimal:** No clutter, focus on essential actions
- **Progressive Disclosure:** Show complexity only when needed
- **Visual Hierarchy:** Important info stands out
- **Confidence-Building:** Clear feedback, helpful guidance
- **Delightful:** Small touches that make setup pleasant

### Functional Goals
- **One-click access** to provider signup pages
- **Inline validation** of API keys
- **Quick testing** (send test request)
- **Clear pricing info** for each provider
- **Smart recommendations** based on use case

---

## UX Design: Provider Settings

### Overall Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Settings > Providers                              [ × ] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  🔍 Search providers...                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Filter by:  [All] [Cloud] [Local] [Configured]        │
│                                                         │
│  ┌─── Popular Providers ──────────────────────────┐    │
│  │                                                 │    │
│  │  ⭐ Recommended for you                         │    │
│  │  Based on: Chinese content, Academic domain    │    │
│  │                                                 │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │ 🇨🇳 Qwen (Dashscope)          [✓ Active] │  │    │
│  │  │ Best for Chinese content                 │  │    │
│  │  │ • Fast • Affordable • High Quality       │  │    │
│  │  │                                          │  │    │
│  │  │ [Configure]                  [Test API]  │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─── All Providers (100+) ───────────────────────┐    │
│  │                                                 │    │
│  │  Cloud Providers (12 configured / 100 total)   │    │
│  │                                                 │    │
│  │  [Provider Card Grid - see below]              │    │
│  │                                                 │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Provider Card Design

### Card States

#### State 1: Not Configured (Default)
```
┌────────────────────────────────────────────┐
│ 🔵 Anthropic                    [Configure]│
│                                            │
│ Claude 3.5 Sonnet, Opus, Haiku            │
│ Best for: Coding, reasoning, creativity   │
│                                            │
│ Pricing: $3-15 per million tokens         │
│ Speed: ⚡⚡⚡ Very Fast                     │
│                                            │
│ 🔗 Get API Key →                           │
└────────────────────────────────────────────┘
```

#### State 2: Configuring (Modal/Slide-in Panel)
```
┌────────────────────────────────────────────────────┐
│ Configure Anthropic                          [ × ] │
├────────────────────────────────────────────────────┤
│                                                    │
│ Step 1: Get Your API Key                          │
│ ┌────────────────────────────────────────────┐    │
│ │ 1. Visit console.anthropic.com             │    │
│ │ 2. Sign up or log in                       │    │
│ │ 3. Go to API Keys section                  │    │
│ │ 4. Create new key                          │    │
│ │                                            │    │
│ │     [🔗 Open Anthropic Console]            │    │
│ └────────────────────────────────────────────┘    │
│                                                    │
│ Step 2: Enter Your API Key                        │
│ ┌────────────────────────────────────────────┐    │
│ │ API Key                                    │    │
│ │ [sk-ant-********************************]  │    │
│ │                                            │    │
│ │ 💡 Your key is encrypted and stored        │    │
│ │    securely on your device                 │    │
│ └────────────────────────────────────────────┘    │
│                                                    │
│ Step 3: Test Connection (Optional)                │
│ ┌────────────────────────────────────────────┐    │
│ │ [🧪 Test API Key]                          │    │
│ │                                            │    │
│ │ Status: ✓ Connected successfully           │    │
│ │ Model: claude-3-5-sonnet-20241022          │    │
│ │ Response time: 342ms                       │    │
│ └────────────────────────────────────────────┘    │
│                                                    │
│              [Cancel]  [Save Configuration]       │
└────────────────────────────────────────────────────┘
```

#### State 3: Configured & Active
```
┌────────────────────────────────────────────┐
│ ✓ Anthropic                    [Edit] [✓]  │
│                                            │
│ Claude 3.5 Sonnet, Opus, Haiku            │
│ Status: ✓ Active (342ms latency)          │
│                                            │
│ This Month: $12.50 / $100 budget          │
│ ├──────────┤ 12.5% used                   │
│                                            │
│ Models: 3 available                        │
│ Last tested: 2 minutes ago                │
│                                            │
│ [Test Again]  [View Usage]  [Disable]     │
└────────────────────────────────────────────┘
```

#### State 4: Error State
```
┌────────────────────────────────────────────┐
│ ⚠️ Anthropic                    [Fix] [×]  │
│                                            │
│ Claude 3.5 Sonnet, Opus, Haiku            │
│ Status: ❌ Authentication failed           │
│                                            │
│ Error: Invalid API key (401)              │
│ Your API key may be expired or invalid.   │
│                                            │
│ [Update Key]  [Test Again]  [Get Help]    │
└────────────────────────────────────────────┘
```

---

## Provider Categories & Organization

### Category 1: Top Tier (Most Popular)
```
┌─── Top Providers ─────────────────────────┐
│                                           │
│ ⭐ Anthropic (Claude)                     │
│ ⭐ OpenAI (GPT-4)                         │
│ ⭐ Google (Gemini)                        │
│ ⭐ Qwen (Dashscope)                       │
│ ⭐ Ollama (Local)                         │
│                                           │
└───────────────────────────────────────────┘
```

### Category 2: By Region
```
┌─── Chinese Providers ─────────────────────┐
│ 🇨🇳 Qwen (Dashscope)                      │
│ 🇨🇳 MiniMax                               │
│ 🇨🇳 GLM (Zhipu AI)                        │
│ 🇨🇳 Baidu (Ernie)                         │
│ 🇨🇳 ByteDance (Doubao)                    │
└───────────────────────────────────────────┘

┌─── US Providers ──────────────────────────┐
│ 🇺🇸 OpenAI                                │
│ 🇺🇸 Anthropic                             │
│ 🇺🇸 Cohere                                │
│ 🇺🇸 Perplexity                            │
└───────────────────────────────────────────┘

┌─── European Providers ────────────────────┐
│ 🇫🇷 Mistral                               │
│ 🇩🇪 Aleph Alpha                           │
└───────────────────────────────────────────┘
```

### Category 3: By Use Case
```
┌─── Best for Coding ───────────────────────┐
│ • Anthropic Claude                        │
│ • OpenAI GPT-4                            │
│ • Qwen Coder                              │
└───────────────────────────────────────────┘

┌─── Best for Chinese ──────────────────────┐
│ • Qwen (Dashscope)                        │
│ • GLM (Zhipu)                             │
│ • MiniMax                                 │
└───────────────────────────────────────────┘

┌─── Best for Privacy ──────────────────────┐
│ • Ollama (Local)                          │
│ • LM Studio (Local)                       │
└───────────────────────────────────────────┘
```

### Category 4: By Cost
```
┌─── Free Tier Available ───────────────────┐
│ 🆓 Ollama (Local - Unlimited)             │
│ 🆓 Google Gemini (Free tier)              │
│ 🆓 OpenRouter (Trial credits)             │
└───────────────────────────────────────────┘

┌─── Most Affordable ───────────────────────┐
│ 💰 Qwen ($0.0007 per 1K tokens)           │
│ 💰 Google Gemini Flash                    │
│ 💰 Mistral                                │
└───────────────────────────────────────────┘
```

---

## Provider Directory (100+ from LiteLLM)

### Master Provider List with Metadata

```yaml
providers:
  # Tier 1: Major Cloud Providers
  anthropic:
    name: "Anthropic"
    display_name: "Anthropic (Claude)"
    icon: "🔵"
    region: "US"
    type: "cloud"
    signup_url: "https://console.anthropic.com/signup"
    dashboard_url: "https://console.anthropic.com/account/keys"
    docs_url: "https://docs.anthropic.com/"
    
    models:
      - "claude-3-5-sonnet-20241022"
      - "claude-3-opus-20240229"
      - "claude-3-haiku-20240307"
    
    pricing:
      input: "$3 per million tokens"
      output: "$15 per million tokens"
      tier: "premium"
    
    strengths:
      - "Reasoning"
      - "Coding"
      - "Long context"
    
    use_cases:
      - "coding"
      - "reasoning"
      - "creative"
    
    speed: "very_fast"  # very_fast, fast, medium, slow
    popularity: "top"   # top, popular, emerging, niche
    
    setup:
      env_var: "ANTHROPIC_API_KEY"
      config_key: "api_key"
      validation_endpoint: "/v1/messages"
    
    free_tier: false
    trial_credits: "$5"

  openai:
    name: "OpenAI"
    display_name: "OpenAI (GPT-4)"
    icon: "🟢"
    region: "US"
    type: "cloud"
    signup_url: "https://platform.openai.com/signup"
    dashboard_url: "https://platform.openai.com/api-keys"
    docs_url: "https://platform.openai.com/docs"
    
    models:
      - "gpt-4-turbo"
      - "gpt-4"
      - "gpt-3.5-turbo"
    
    pricing:
      input: "$10 per million tokens"
      output: "$30 per million tokens"
      tier: "premium"
    
    strengths:
      - "General purpose"
      - "Multimodal"
      - "Function calling"
    
    use_cases:
      - "general"
      - "coding"
      - "multimodal"
    
    speed: "fast"
    popularity: "top"
    
    setup:
      env_var: "OPENAI_API_KEY"
      config_key: "api_key"
      validation_endpoint: "/v1/models"
    
    free_tier: false
    trial_credits: "$5"

  qwen:
    name: "Qwen"
    display_name: "Qwen (Dashscope)"
    icon: "🇨🇳"
    region: "China"
    type: "cloud"
    signup_url: "https://dashscope.console.aliyun.com/"
    dashboard_url: "https://dashscope.console.aliyun.com/apiKey"
    docs_url: "https://help.aliyun.com/zh/dashscope/"
    
    models:
      - "qwen-turbo"
      - "qwen-plus"
      - "qwen-max"
    
    pricing:
      input: "¥0.0007 per 1K tokens"
      output: "¥0.002 per 1K tokens"
      tier: "affordable"
    
    strengths:
      - "Chinese language"
      - "Multilingual"
      - "Cost-effective"
    
    use_cases:
      - "chinese"
      - "multilingual"
      - "general"
    
    speed: "very_fast"
    popularity: "popular"
    
    setup:
      env_var: "DASHSCOPE_API_KEY"
      config_key: "api_key"
      validation_endpoint: "/compatible-mode/v1/models"
    
    free_tier: true
    trial_credits: "¥100"

  ollama:
    name: "Ollama"
    display_name: "Ollama (Local)"
    icon: "🦙"
    region: "Local"
    type: "local"
    signup_url: null  # No signup needed
    dashboard_url: null
    docs_url: "https://ollama.ai/docs"
    
    models:
      - "llama3.2:3b"
      - "llama3:8b"
      - "codellama"
      - "mistral"
    
    pricing:
      input: "Free (local compute)"
      output: "Free (local compute)"
      tier: "free"
    
    strengths:
      - "Privacy"
      - "Offline"
      - "No cost"
    
    use_cases:
      - "privacy"
      - "offline"
      - "development"
    
    speed: "fast"  # Depends on hardware
    popularity: "top"
    
    setup:
      env_var: null
      config_key: "host"
      validation_endpoint: "/api/tags"
      default_host: "http://localhost:11434"
    
    free_tier: true
    trial_credits: null

  # ... 96+ more providers following same schema
```

---

## Interactive Setup Flow

### Flow 1: First-Time Setup Wizard

```
┌─────────────────────────────────────────────────────┐
│ Welcome to Polly Provider Setup                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Let's get you started with AI providers.           │
│ This will take about 2 minutes.                    │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │                                             │   │
│ │     [🦙]  Start with Local (Free)           │   │
│ │                                             │   │
│ │     Set up Ollama on your computer          │   │
│ │     • No API keys needed                    │   │
│ │     • 100% private                          │   │
│ │     • Works offline                         │   │
│ │                                             │   │
│ │     [Get Started]                           │   │
│ │                                             │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │                                             │   │
│ │     [☁️]  Add Cloud Provider                │   │
│ │                                             │   │
│ │     Connect to Anthropic, OpenAI, etc.      │   │
│ │     • Better quality                        │   │
│ │     • More models                           │   │
│ │     • Requires API key                      │   │
│ │                                             │   │
│ │     [Browse Providers]                      │   │
│ │                                             │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│                         [Skip Setup - Use Later]   │
└─────────────────────────────────────────────────────┘
```

### Flow 2: Ollama Local Setup

```
┌─────────────────────────────────────────────────────┐
│ Set Up Ollama (Local)                         [×]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Step 1: Install Ollama                             │
│ ┌─────────────────────────────────────────────┐   │
│ │ ○ Checking if Ollama is installed...       │   │
│ │                                             │   │
│ │ ✓ Ollama detected at localhost:11434       │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ Step 2: Download Models                            │
│ ┌─────────────────────────────────────────────┐   │
│ │ Recommended models:                         │   │
│ │                                             │   │
│ │ ☑ llama3.2:3b (2.0GB) - Fast, general      │   │
│ │ ☐ llama3:8b (4.7GB) - Better quality       │   │
│ │ ☐ nomic-embed-text (274MB) - Embeddings    │   │
│ │                                             │   │
│ │ [Download Selected Models]                  │   │
│ │                                             │   │
│ │ Progress: ████████░░ 80%                    │   │
│ │ Downloading llama3.2:3b (1.6GB / 2.0GB)    │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ Step 3: Test                                       │
│ ┌─────────────────────────────────────────────┐   │
│ │ [🧪 Test Connection]                        │   │
│ │                                             │   │
│ │ ✓ Successfully connected                    │   │
│ │ ✓ Model llama3.2:3b ready                   │   │
│ │ Response time: 1.2s                         │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│                              [Done]                │
└─────────────────────────────────────────────────────┘
```

### Flow 3: Cloud Provider Setup (Qwen Example)

```
┌─────────────────────────────────────────────────────┐
│ Set Up Qwen (Dashscope)                       [×]   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Why Qwen?                                          │
│ • Best Chinese language support                    │
│ • Fast and affordable (¥0.0007 per 1K tokens)     │
│ • Free trial with ¥100 credits                    │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ Step 1: Create Account                      │   │
│ │                                             │   │
│ │ Visit Dashscope Console:                    │   │
│ │ [🔗 Open dashscope.console.aliyun.com]      │   │
│ │                                             │   │
│ │ 💡 Tip: You'll need a Chinese phone number │   │
│ │    or Aliyun account                        │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ Step 2: Get API Key                         │   │
│ │                                             │   │
│ │ 1. Log in to Dashscope Console              │   │
│ │ 2. Click "API Key" in left sidebar          │   │
│ │ 3. Click "Create New Key"                   │   │
│ │ 4. Copy the key                             │   │
│ │                                             │   │
│ │ [🔗 Open API Key Page]                      │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ Step 3: Enter API Key                       │   │
│ │                                             │   │
│ │ [sk-************************************************] │
│ │                                             │   │
│ │ 🔒 Encrypted and stored locally             │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ Step 4: Test Connection                     │   │
│ │                                             │   │
│ │ [🧪 Test API Key]                           │   │
│ │                                             │   │
│ │ Testing... ⏳                                │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│                    [Cancel]  [Save & Continue]     │
└─────────────────────────────────────────────────────┘
```

---

## Provider Search & Discovery

### Smart Search Interface

```
┌─────────────────────────────────────────────────────┐
│ 🔍 Search providers...                              │
│                                                     │
│ [chinese language                         ] [×]     │
└─────────────────────────────────────────────────────┘

Results for "chinese language":

┌─── Best Match ────────────────────────────────────┐
│ 🇨🇳 Qwen (Dashscope)                    [Configure]│
│ Specifically optimized for Chinese text           │
│ ⭐⭐⭐⭐⭐ 98% match                               │
└───────────────────────────────────────────────────┘

┌─── Good Match ────────────────────────────────────┐
│ 🇨🇳 GLM (Zhipu AI)                      [Configure]│
│ Strong Chinese support, academic focus            │
│ ⭐⭐⭐⭐ 85% match                                 │
└───────────────────────────────────────────────────┘

┌─── Also Consider ─────────────────────────────────┐
│ 🇨🇳 MiniMax                             [Configure]│
│ Chinese with multimodal capabilities              │
│ ⭐⭐⭐ 72% match                                   │
└───────────────────────────────────────────────────┘
```

### Filter & Sort

```
┌─────────────────────────────────────────────────────┐
│ Providers (showing 12 of 100+)                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Filter by:                                          │
│ ☑ Cloud  ☑ Local  ☑ Chinese  ☐ US  ☐ EU          │
│                                                     │
│ Sort by:                                            │
│ ● Recommended  ○ Price  ○ Speed  ○ Popularity      │
│                                                     │
│ Cost range:                                         │
│ ● Free  ● Affordable  ○ Premium  ○ Enterprise      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Implementation: Provider Metadata Service

### File Structure

```
core/providers/
├── provider_registry.py      # Main registry
├── provider_metadata.yaml    # All provider configs
├── provider_validator.py     # API key validation
├── provider_categories.py    # Categorization logic
└── setup_wizard.py           # First-time setup flow

electron-app/src/renderer/
├── settings-providers.js     # Main settings UI
├── provider-card.js          # Provider card component
├── setup-wizard.js           # Setup wizard component
└── api-key-manager.js        # Key management logic
```

### Backend: Provider Registry

```python
# core/providers/provider_registry.py

from typing import Dict, List, Optional
import yaml
from pathlib import Path

class ProviderRegistry:
    """
    Central registry for all LiteLLM providers with rich metadata.
    """
    
    def __init__(self):
        self.providers = self._load_providers()
    
    def _load_providers(self) -> Dict:
        """Load provider metadata from YAML."""
        metadata_path = Path(__file__).parent / "provider_metadata.yaml"
        with open(metadata_path) as f:
            return yaml.safe_load(f)
    
    def get_all_providers(self) -> List[Dict]:
        """Get all providers with metadata."""
        return list(self.providers.values())
    
    def get_provider(self, name: str) -> Optional[Dict]:
        """Get specific provider by name."""
        return self.providers.get(name)
    
    def search_providers(self, query: str) -> List[Dict]:
        """
        Search providers by name, use case, or description.
        
        Returns providers sorted by relevance score.
        """
        query_lower = query.lower()
        results = []
        
        for name, provider in self.providers.items():
            score = 0
            
            # Name match (highest priority)
            if query_lower in provider['name'].lower():
                score += 100
            
            # Use case match
            for use_case in provider.get('use_cases', []):
                if query_lower in use_case.lower():
                    score += 50
            
            # Strengths match
            for strength in provider.get('strengths', []):
                if query_lower in strength.lower():
                    score += 30
            
            # Region match
            if query_lower in provider.get('region', '').lower():
                score += 20
            
            if score > 0:
                results.append({
                    'provider': provider,
                    'score': score,
                    'name': name
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return [r['provider'] for r in results]
    
    def filter_providers(self, 
                         type: Optional[str] = None,
                         region: Optional[str] = None,
                         use_case: Optional[str] = None,
                         free_tier: Optional[bool] = None) -> List[Dict]:
        """
        Filter providers by criteria.
        """
        filtered = []
        
        for name, provider in self.providers.items():
            # Type filter
            if type and provider.get('type') != type:
                continue
            
            # Region filter
            if region and provider.get('region') != region:
                continue
            
            # Use case filter
            if use_case and use_case not in provider.get('use_cases', []):
                continue
            
            # Free tier filter
            if free_tier is not None and provider.get('free_tier') != free_tier:
                continue
            
            filtered.append(provider)
        
        return filtered
    
    def get_recommended_providers(self, context: Dict) -> List[Dict]:
        """
        Get recommended providers based on user context.
        
        Args:
            context: {
                'language': 'chinese' | 'english' | 'multilingual',
                'domain': 'academic' | 'coding' | 'general',
                'privacy': 'high' | 'medium' | 'low',
                'budget': 'free' | 'affordable' | 'premium'
            }
        """
        recommendations = []
        
        # Language-based recommendations
        if context.get('language') == 'chinese':
            recommendations.extend(['qwen', 'glm', 'minimax'])
        
        # Privacy-based recommendations
        if context.get('privacy') == 'high':
            recommendations.extend(['ollama'])
        
        # Budget-based recommendations
        if context.get('budget') == 'free':
            recommendations.extend(['ollama', 'google'])
        elif context.get('budget') == 'affordable':
            recommendations.extend(['qwen', 'mistral'])
        
        # Domain-based recommendations
        if context.get('domain') == 'academic':
            recommendations.extend(['glm', 'anthropic'])
        elif context.get('domain') == 'coding':
            recommendations.extend(['anthropic', 'openai'])
        
        # Return unique providers in recommendation order
        seen = set()
        result = []
        for name in recommendations:
            if name not in seen and name in self.providers:
                seen.add(name)
                result.append(self.providers[name])
        
        return result
```

### Backend: API Key Validator

```python
# core/providers/provider_validator.py

import httpx
import os
from typing import Dict, Tuple

class ProviderValidator:
    """
    Validate API keys for providers.
    """
    
    async def validate_key(self, provider: str, api_key: str) -> Tuple[bool, str, Dict]:
        """
        Validate an API key for a provider.
        
        Returns:
            (is_valid, message, details)
        """
        validators = {
            'anthropic': self._validate_anthropic,
            'openai': self._validate_openai,
            'qwen': self._validate_qwen,
            'google': self._validate_google,
            'ollama': self._validate_ollama,
            # ... add all providers
        }
        
        validator = validators.get(provider)
        if not validator:
            return (False, f"No validator for {provider}", {})
        
        return await validator(api_key)
    
    async def _validate_anthropic(self, api_key: str) -> Tuple[bool, str, Dict]:
        """Validate Anthropic API key."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "test"}]
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return (True, "API key is valid", {
                        "latency_ms": response.elapsed.total_seconds() * 1000,
                        "model": "claude-3-haiku-20240307"
                    })
                elif response.status_code == 401:
                    return (False, "Invalid API key", {})
                else:
                    return (False, f"Error: {response.status_code}", {})
        
        except Exception as e:
            return (False, f"Connection error: {str(e)}", {})
    
    async def _validate_qwen(self, api_key: str) -> Tuple[bool, str, Dict]:
        """Validate Qwen/Dashscope API key."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    models = response.json().get('data', [])
                    return (True, "API key is valid", {
                        "latency_ms": response.elapsed.total_seconds() * 1000,
                        "models_available": len(models)
                    })
                elif response.status_code == 401:
                    return (False, "Invalid API key", {})
                else:
                    return (False, f"Error: {response.status_code}", {})
        
        except Exception as e:
            return (False, f"Connection error: {str(e)}", {})
    
    async def _validate_ollama(self, host: str = "http://localhost:11434") -> Tuple[bool, str, Dict]:
        """Validate Ollama is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{host}/api/tags", timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    return (True, f"Ollama is running with {len(models)} models", {
                        "latency_ms": response.elapsed.total_seconds() * 1000,
                        "models_available": len(models),
                        "models": [m['name'] for m in models]
                    })
                else:
                    return (False, f"Error: {response.status_code}", {})
        
        except Exception as e:
            return (False, "Ollama is not running. Please start Ollama first.", {})
    
    # Add validators for all 100+ providers...
```

### Frontend: Provider Settings Component

```javascript
// electron-app/src/renderer/settings-providers.js

class ProviderSettingsManager {
    constructor() {
        this.registry = null;
        this.validator = null;
        this.configured = new Set();
        
        this.init();
    }
    
    async init() {
        // Load provider registry from backend
        this.registry = await this.fetchProviderRegistry();
        
        // Load configured providers
        this.configured = await this.fetchConfiguredProviders();
        
        // Render UI
        this.render();
    }
    
    async fetchProviderRegistry() {
        const response = await fetch('/api/providers/registry');
        return await response.json();
    }
    
    async fetchConfiguredProviders() {
        const response = await fetch('/api/providers/configured');
        const data = await response.json();
        return new Set(data.providers);
    }
    
    render() {
        const container = document.getElementById('provider-settings');
        
        // Search bar
        const searchBar = this.renderSearchBar();
        
        // Filters
        const filters = this.renderFilters();
        
        // Recommended section
        const recommended = this.renderRecommended();
        
        // All providers grid
        const providersGrid = this.renderProvidersGrid();
        
        container.innerHTML = `
            ${searchBar}
            ${filters}
            ${recommended}
            ${providersGrid}
        `;
        
        this.attachEventListeners();
    }
    
    renderSearchBar() {
        return `
            <div class="search-container">
                <input 
                    type="text" 
                    id="provider-search" 
                    placeholder="🔍 Search providers..."
                    class="provider-search-input"
                />
            </div>
        `;
    }
    
    renderFilters() {
        return `
            <div class="filter-container">
                <div class="filter-group">
                    <span class="filter-label">Filter by:</span>
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="cloud">Cloud</button>
                    <button class="filter-btn" data-filter="local">Local</button>
                    <button class="filter-btn" data-filter="configured">Configured</button>
                </div>
                
                <div class="sort-group">
                    <span class="sort-label">Sort by:</span>
                    <select id="sort-select" class="sort-select">
                        <option value="recommended">Recommended</option>
                        <option value="price">Price</option>
                        <option value="speed">Speed</option>
                        <option value="popularity">Popularity</option>
                    </select>
                </div>
            </div>
        `;
    }
    
    renderRecommended() {
        // Get user context
        const context = this.getUserContext();
        
        // Get recommendations from backend
        const recommended = this.getRecommendedProviders(context);
        
        if (recommended.length === 0) {
            return '';
        }
        
        return `
            <div class="recommended-section">
                <h3>⭐ Recommended for you</h3>
                <p class="recommendation-reason">
                    Based on: ${this.getRecommendationReason(context)}
                </p>
                <div class="provider-cards-horizontal">
                    ${recommended.map(p => this.renderProviderCard(p, true)).join('')}
                </div>
            </div>
        `;
    }
    
    renderProvidersGrid() {
        const providers = this.getFilteredProviders();
        
        return `
            <div class="providers-section">
                <h3>All Providers (${providers.length} / 100+)</h3>
                <div class="provider-cards-grid">
                    ${providers.map(p => this.renderProviderCard(p)).join('')}
                </div>
            </div>
        `;
    }
    
    renderProviderCard(provider, compact = false) {
        const isConfigured = this.configured.has(provider.name);
        const statusBadge = isConfigured ? 
            '<span class="status-badge configured">✓ Active</span>' :
            '<span class="status-badge unconfigured">Configure</span>';
        
        return `
            <div class="provider-card ${compact ? 'compact' : ''}" data-provider="${provider.name}">
                <div class="card-header">
                    <span class="provider-icon">${provider.icon}</span>
                    <h4 class="provider-name">${provider.display_name}</h4>
                    ${statusBadge}
                </div>
                
                <div class="card-body">
                    <p class="provider-description">
                        ${provider.models.slice(0, 2).join(', ')}
                    </p>
                    
                    <div class="provider-tags">
                        ${provider.strengths.slice(0, 3).map(s => 
                            `<span class="tag">${s}</span>`
                        ).join('')}
                    </div>
                    
                    <div class="provider-info">
                        <div class="info-row">
                            <span class="label">Pricing:</span>
                            <span class="value">${provider.pricing.input}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Speed:</span>
                            <span class="value">${this.renderSpeedIndicator(provider.speed)}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-footer">
                    ${isConfigured ? 
                        `<button class="btn-secondary" onclick="providerManager.editProvider('${provider.name}')">Edit</button>
                         <button class="btn-secondary" onclick="providerManager.testProvider('${provider.name}')">Test</button>` :
                        `<button class="btn-primary" onclick="providerManager.configureProvider('${provider.name}')">Configure</button>
                         <a href="${provider.signup_url}" target="_blank" class="link-external">🔗 Get API Key →</a>`
                    }
                </div>
            </div>
        `;
    }
    
    async configureProvider(providerName) {
        const provider = this.registry[providerName];
        
        // Show configuration modal
        const modal = new ProviderConfigModal(provider, this.validator);
        const result = await modal.show();
        
        if (result.success) {
            // Save configuration
            await this.saveProviderConfig(providerName, result.config);
            
            // Update UI
            this.configured.add(providerName);
            this.render();
            
            // Show success message
            this.showNotification(`✓ ${provider.display_name} configured successfully!`);
        }
    }
    
    // ... more methods
}
```

---

## Continued in next file...

This is getting very long. Should I:
1. Continue with the CSS styling and complete implementation
2. Create a separate file for the UI styling guide
3. Move to a summary document

What would you prefer?
