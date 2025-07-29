import pickle
from app.models import is_even, reverse_text

with open('is_even.pkl', 'wb') as f:
    pickle.dump(is_even, f)

with open('text_reverser.pkl', 'wb') as f:
    pickle.dump(reverse_text, f)

print("Models created successfully: is_even.pkl, text_reverser.pkl")
