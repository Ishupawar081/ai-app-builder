from dotenv import load_dotenv
import os
import json
import re
import time
import google.generativeai as genai

# 🔹 Load environment variables (.env file)
load_dotenv()

# 🔥 CACHE
# Stores generated plans and code to avoid repeated API calls
CACHE = {}


# 🔥 INIT MODEL
def get_model():
    """
    Initialize Gemini LLM model using API key
    """
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")

    # Safety check
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")

    # Configure Gemini SDK
    genai.configure(api_key=api_key)

    # Return model instance
    return genai.GenerativeModel("gemini-2.5-flash")


# 🔥 CLEAN JSON (SAFER)
def extract_json(text: str):
    """
    Extract JSON object from LLM response
    Handles markdown wrapping and extra text
    """
    text = text.strip()

    # Remove markdown code blocks if present
    text = text.replace("```json", "").replace("```", "")

    # Extract JSON using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)

    return match.group(0) if match else text


# 🔥 FIX JSON (IMPROVED)
def fix_json(text: str):
    """
    Fix common JSON issues from LLM output
    - Missing braces
    - Trailing commas
    """
    text = text.strip()

    # Count opening and closing braces
    open_braces = text.count("{")
    close_braces = text.count("}")

    # Add missing closing braces
    if open_braces > close_braces:
        text += "}" * (open_braces - close_braces)

    # Remove trailing commas (invalid in JSON)
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    return text


# 🔥 GENERIC LLM CALL (WITH RETRY + BACKOFF)
def call_llm(prompt: str):
    """
    Calls LLM with retry logic
    Handles rate limits and failures
    """
    model = get_model()

    # Retry up to 3 times
    for attempt in range(3):
        try:
            # Send prompt to LLM
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            err = str(e).lower()

            # Handle rate limit errors
            if "429" in err or "quota" in err:
                wait = 5 * (attempt + 1)
                print(f"⚠️ Rate limit. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e

    return None


# 🔥 STEP 1: PLAN GENERATION
def generate_plan(user_prompt: str):
    """
    Converts user input into structured JSON plan
    """

    # Use cache if already generated
    if user_prompt in CACHE:
        print("⚡ Using cached plan")
        return CACHE[user_prompt]

    # Prompt for LLM to generate structured plan
    prompt = f"""
You are an expert frontend system designer.

Convert the user idea into a structured app plan.

Return ONLY valid JSON.

STRICT RULES:
- No explanation
- No markdown
- No trailing commas

FORMAT:
{{
  "app_name": "",
  "app_type": "",
  "pages": [],
  "components": [],
  "data_model": {{
    "entities": []
  }},
  "interactions": [],
  "acceptance_criteria": [],
  "assumptions": [],
  "questions": []
}}

User idea:
{user_prompt}
"""

    # Call LLM
    raw = call_llm(prompt)

    if not raw:
        return {"error": "LLM failed"}

    # Extract JSON part
    content = extract_json(raw)

    try:
        # Try parsing JSON directly
        plan = json.loads(content)

        # Store in cache
        CACHE[user_prompt] = plan
        return plan

    except:
        # Try fixing JSON if parsing fails
        fixed = fix_json(content)

        try:
            plan = json.loads(fixed)
            CACHE[user_prompt] = plan
            return plan

        except:
            # Return debug info if still invalid
            return {
                "error": "Invalid JSON",
                "raw": raw,
                "cleaned": content,
                "fixed": fixed
            }


# 🔥 STEP 2: CODE GENERATION (HIGHLY CONTROLLED)
def generate_react_app(plan: dict):
    """
    Converts structured plan into React App.jsx code
    """

    # Create cache key for plan
    cache_key = f"code::{json.dumps(plan)}"

    # Return cached code if available
    if cache_key in CACHE:
        print("⚡ Using cached code")
        return CACHE[cache_key]

    # Prompt for generating React app
    prompt = f"""
You are a senior React developer AND UI/UX designer.

Generate a CLEAN, WELL-STRUCTURED React App.jsx.

🔥 STRICT CODE RULES:
- Do NOT use invalid JS syntax
- Do NOT use CSS pseudo selectors like &:focus
- Use ONLY valid inline styles
- Ensure NO typos in variable names
- Ensure JSX is valid
- Avoid overly complex logic

✅ STRUCTURE:
- Sidebar (left)
- Main content (right)
- Header in main content
- Clear sections

✅ UI:
- Flexbox layout
- Padding: 20
- Clean spacing
- No overlap
- Soft colors (#1e293b, #f1f5f9, white)
- Rounded corners
- Simple shadows

✅ FUNCTIONALITY:
- Fully implement plan
- Must be interactive
- No blank screens

---

🔥 BASE LAYOUT:

<div style={{
  display: "flex",
  height: "100vh",
  fontFamily: "Arial"
}}>

  <div style={{
    width: "250px",
    background: "#1e293b",
    color: "white",
    padding: 20
  }}>
    Sidebar
  </div>

  <div style={{
    flex: 1,
    padding: 20,
    background: "#f1f5f9"
  }}>
    Main Content
  </div>

</div>

---

PLAN:
{json.dumps(plan, indent=2)}

---

STRICT:
- Return ONLY code
- No markdown
- No explanation
"""

    # Call LLM to generate code
    raw = call_llm(prompt)

    if not raw:
        return None

    # Clean markdown formatting if present
    code = raw.replace("```jsx", "").replace("```", "").strip()

    # Basic validation check
    if "function App" not in code:
        print("⚠️ Generated code invalid")
        return None

    # Store in cache
    CACHE[cache_key] = code

    return code