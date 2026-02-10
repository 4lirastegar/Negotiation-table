"""
Helper script to download NLTK data with SSL verification disabled
This is needed for Flesch readability metrics
"""
import ssl
import nltk

# Disable SSL verification (workaround for certificate issues)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
print("Downloading NLTK data for Flesch metrics...")
print("-" * 50)

# Download punkt (for tokenization)
print("\n1. Downloading 'punkt' (tokenizer)...")
nltk.download('punkt')

# Download punkt_tab (newer version)
print("\n2. Downloading 'punkt_tab' (tokenizer tables)...")
nltk.download('punkt_tab')

# Download cmudict (for syllable counting - needed for Flesch!)
print("\n3. Downloading 'cmudict' (syllable dictionary)...")
nltk.download('cmudict')

print("\n" + "=" * 50)
print("✅ NLTK data download complete!")
print("=" * 50)
