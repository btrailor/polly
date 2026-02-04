"""
LLM-powered natural language file organization system.

This module enables Polly to understand and execute file organization requests
in natural language, parsing commands into structured operations.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


FILESYSTEM_SYSTEM_PROMPT = """You are Polly's file system organization assistant. Your role is to help users organize their macOS files by interpreting their natural language requests and converting them into structured file operations.

## Available Operations

1. **create_folder**: Create a new folder
   - Parameters: path, parents (bool)

2. **move**: Move files to a new location
   - Parameters: source, destination, overwrite (bool)

3. **rename**: Rename a file or folder
   - Parameters: path, new_name

4. **tag**: Add macOS Finder tags to files
   - Parameters: path, tags (list)
   - Available color tags: red, orange, yellow, green, blue, purple, gray
   - Can also use custom text labels

5. **batch_organize**: Organize multiple files with rules
   - Parameters: source_dir, rules (list of rule objects)
   - Rule format: {"pattern": "*.ext", "action": "move/tag", "destination": "path", "tags": ["list"]}

## Safety Guidelines

1. **ALWAYS use dry_run: true** for the first pass to preview operations
2. **NEVER modify** these protected directories:
   - /System, /Library, /usr, /bin, /sbin, /private, /Applications, /.Trash
3. **Warn about** sensitive directories:
   - ~/Library, ~/Documents, ~/Desktop
4. **Batch operations** over 100 files require explicit confirmation
5. **Expand paths**: Convert relative paths to absolute (~ to home directory)

## Response Format

You must respond with a JSON object in this format:

```json
{
  "understood": "Brief summary of what the user wants to do",
  "operations": [
    {
      "type": "create_folder|move|rename|tag|batch_organize",
      "params": {
        // Operation-specific parameters
      }
    }
  ],
  "dry_run": true,
  "requires_confirmation": true/false,
  "warnings": ["List of any warnings about the operations"]
}
```

## Examples

User: "Organize my Downloads folder by file type"
Response:
```json
{
  "understood": "Create folders for different file types in Downloads and move files accordingly",
  "operations": [
    {"type": "create_folder", "params": {"path": "~/Downloads/PDFs", "parents": true}},
    {"type": "create_folder", "params": {"path": "~/Downloads/Images", "parents": true}},
    {"type": "create_folder", "params": {"path": "~/Downloads/Documents", "parents": true}},
    {"type": "batch_organize", "params": {
      "source_dir": "~/Downloads",
      "rules": [
        {"pattern": "*.pdf", "action": "move", "destination": "~/Downloads/PDFs"},
        {"pattern": "*.{jpg,jpeg,png,gif}", "action": "move", "destination": "~/Downloads/Images"},
        {"pattern": "*.{doc,docx,txt}", "action": "move", "destination": "~/Downloads/Documents"}
      ]
    }}
  ],
  "dry_run": true,
  "requires_confirmation": true,
  "warnings": []
}
```

User: "Tag all PDFs on my Desktop with 'work' and blue"
Response:
```json
{
  "understood": "Add 'work' and blue tags to all PDF files on Desktop",
  "operations": [
    {"type": "batch_organize", "params": {
      "source_dir": "~/Desktop",
      "rules": [
        {"pattern": "*.pdf", "action": "tag", "tags": ["work", "blue"]}
      ]
    }}
  ],
  "dry_run": true,
  "requires_confirmation": false,
  "warnings": []
}
```

User: "Move all images from last week to Photos/2026"
Response:
```json
{
  "understood": "Move recent image files to Photos/2026 folder",
  "operations": [
    {"type": "create_folder", "params": {"path": "~/Photos/2026", "parents": true}},
    {"type": "batch_organize", "params": {
      "source_dir": "~/Desktop",
      "rules": [
        {"pattern": "*.{jpg,jpeg,png,gif,heic}", "action": "move", "destination": "~/Photos/2026"}
      ]
    }}
  ],
  "dry_run": true,
  "requires_confirmation": true,
  "warnings": ["This will move all matching images. Review the dry-run results before confirming."]
}
```

## Important Notes

- Always expand ~ to the user's home directory
- Use glob patterns for file matching (*, ?, [])
- Suggest creating destination folders if they don't exist
- For complex operations, break them into multiple steps
- Always start with dry_run: true
- Provide clear explanations of what will happen
"""


class FileSystemLLMParser:
    """
    Parse natural language file organization requests into structured operations.
    """
    
    def __init__(self, llm_client):
        """
        Initialize the parser with an LLM client.
        
        Args:
            llm_client: LLM client with a generate() method
        """
        self.llm = llm_client
    
    def parse_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse a natural language file organization request.
        
        Args:
            user_request: User's natural language request
            context: Optional context (current directory, recent operations, etc.)
            
        Returns:
            Parsed operation plan as dict
        """
        # Build the full prompt
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n"
            if "current_dir" in context:
                context_str += f"- Current directory: {context['current_dir']}\n"
            if "recent_operations" in context:
                context_str += f"- Recent operations: {len(context['recent_operations'])}\n"
        
        user_prompt = f"""User request: {user_request}{context_str}

Please parse this file organization request into a structured operation plan. Return ONLY the JSON object, no markdown formatting or extra text."""
        
        try:
            # Generate response from LLM
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=FILESYSTEM_SYSTEM_PROMPT,
                temperature=0.1,  # Low temperature for structured output
                max_tokens=1000
            )
            
            # Parse JSON response
            # Try to extract JSON if it's wrapped in markdown
            response_text = response.strip()
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                response_text = response_text[start:end].strip()
            
            parsed = json.loads(response_text)
            
            # Validate structure
            required_fields = ["understood", "operations", "dry_run", "requires_confirmation"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            return {
                "error": "Failed to parse operation plan",
                "details": str(e),
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Error parsing request: {e}")
            return {
                "error": "Failed to process request",
                "details": str(e)
            }
    
    def validate_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that operations are safe and well-formed.
        
        Args:
            operations: List of operation dicts
            
        Returns:
            Validation result with any errors or warnings
        """
        errors = []
        warnings = []
        
        for i, op in enumerate(operations):
            op_type = op.get("type")
            params = op.get("params", {})
            
            # Validate operation type
            valid_types = ["create_folder", "move", "rename", "tag", "batch_organize"]
            if op_type not in valid_types:
                errors.append(f"Operation {i}: Invalid type '{op_type}'")
                continue
            
            # Validate parameters based on type
            if op_type == "create_folder":
                if "path" not in params:
                    errors.append(f"Operation {i}: Missing 'path' parameter")
                else:
                    path = Path(params["path"]).expanduser()
                    if str(path).startswith("/System") or str(path).startswith("/Library"):
                        errors.append(f"Operation {i}: Protected path '{path}'")
            
            elif op_type == "move":
                if "source" not in params or "destination" not in params:
                    errors.append(f"Operation {i}: Missing 'source' or 'destination' parameter")
            
            elif op_type == "rename":
                if "path" not in params or "new_name" not in params:
                    errors.append(f"Operation {i}: Missing 'path' or 'new_name' parameter")
            
            elif op_type == "tag":
                if "path" not in params or "tags" not in params:
                    errors.append(f"Operation {i}: Missing 'path' or 'tags' parameter")
                elif not isinstance(params["tags"], list):
                    errors.append(f"Operation {i}: 'tags' must be a list")
            
            elif op_type == "batch_organize":
                if "source_dir" not in params or "rules" not in params:
                    errors.append(f"Operation {i}: Missing 'source_dir' or 'rules' parameter")
                elif not isinstance(params["rules"], list):
                    errors.append(f"Operation {i}: 'rules' must be a list")
                else:
                    # Check batch size
                    if len(params["rules"]) > 100:
                        warnings.append(f"Operation {i}: Large batch ({len(params['rules'])} rules)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def explain_operations(self, operations: List[Dict[str, Any]]) -> str:
        """
        Generate a human-readable explanation of operations.
        
        Args:
            operations: List of operation dicts
            
        Returns:
            Human-readable explanation string
        """
        explanations = []
        
        for i, op in enumerate(operations, 1):
            op_type = op.get("type")
            params = op.get("params", {})
            
            if op_type == "create_folder":
                path = params.get("path", "?")
                explanations.append(f"{i}. Create folder: {path}")
            
            elif op_type == "move":
                src = params.get("source", "?")
                dst = params.get("destination", "?")
                explanations.append(f"{i}. Move: {src} → {dst}")
            
            elif op_type == "rename":
                path = params.get("path", "?")
                new_name = params.get("new_name", "?")
                explanations.append(f"{i}. Rename: {path} → {new_name}")
            
            elif op_type == "tag":
                path = params.get("path", "?")
                tags = params.get("tags", [])
                explanations.append(f"{i}. Tag {path} with: {', '.join(tags)}")
            
            elif op_type == "batch_organize":
                src_dir = params.get("source_dir", "?")
                rules_count = len(params.get("rules", []))
                explanations.append(f"{i}. Organize {src_dir} using {rules_count} rules")
        
        return "\n".join(explanations)


# Helper function for integration with Polly
def parse_filesystem_request(llm_client, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to parse a file system request.
    
    Args:
        llm_client: LLM client instance
        request: Natural language request
        context: Optional context dict
        
    Returns:
        Parsed operation plan
    """
    parser = FileSystemLLMParser(llm_client)
    return parser.parse_request(request, context)
