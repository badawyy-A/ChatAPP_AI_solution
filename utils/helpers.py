import numpy as np
from urllib.parse import urlparse
import re

def extract_features(url):
    shorteners = ['bit.ly', 'goo.gl', 'tinyurl', 'ow.ly', 't.co', 'is.gd', 'buff.ly']
    return np.array([
        [
            len(url),
            url.count('.'),
            1 if re.match(r'^(http[s]?://)?(\d{1,3}\.){3}\d{1,3}', url) else 0,
            url.count('-'),
            url.count('@'),
            url.count('=') + url.count('&') + url.count('%'),
            len(urlparse(url).path),
            len(urlparse(url).query),
            1 if url.startswith('https') else 0,
            1 if any(s in url for s in shorteners) else 0
        ]
    ]) 