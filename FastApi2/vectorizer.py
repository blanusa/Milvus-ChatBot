import pandas as pd
import spacy

# Load the SpaCy model
nlp = spacy.load('en_core_web_lg')

# Read CSV file into a DataFrame
df = pd.read_csv('landmarks.csv')  # Replace with your actual file path

# Check for missing values and fill with empty strings
df['Landmark'] = df['Landmark'].fillna('')

# Process the text data and get vectors
def get_vectors(text):
    if text.strip() == '':
        # Return a zero vector for empty strings
        return [0.0] * nlp.vocab.vectors_length
    try:
        doc = nlp(text)
        return doc.vector
    except Exception as e:
        print(f"Error processing text: {text} - {e}")
        # Return a zero vector if there's an error
        return [0.0] * nlp.vocab.vectors_length

# Apply the get_vectors function to the 'text' column
df['vector'] = df['Landmark'].apply(get_vectors)

# If you want to see the first few vectors along with the text
print(df[['Landmark', 'vector']].head())

# Save the DataFrame with vectors to a new CSV (optional)
df.to_csv('vectorizedLandmarks.csv', index=False)  # Replace with your desired file path
