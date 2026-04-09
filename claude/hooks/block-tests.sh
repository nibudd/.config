#!/bin/bash
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

if echo "$COMMAND" | grep -qE '(^|\s|&&|\|\||;)(pytest|npm test|npx vitest|npx jest|cargo test|go test|make test)(\s|$|;|&&|\|\|)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Test commands are blocked. Run tests manually outside of Claude."
    }
  }'
fi
