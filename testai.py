from google import genai

client = genai.Client(api_key="AIzaSyBhS9kuaDHWFzVYNEgUKyx26nTlB9ti47A")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)
