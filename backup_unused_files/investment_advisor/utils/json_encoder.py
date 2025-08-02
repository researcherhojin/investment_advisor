"""
Custom JSON encoder for handling special data types
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles various data types."""
    
    def default(self, obj):
        """Convert object to JSON serializable format."""
        # Handle pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        
        # Handle datetime
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle numpy types
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # Handle Decimal
        elif isinstance(obj, Decimal):
            return float(obj)
        
        # Handle pandas Series
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        
        # Handle pandas DataFrame
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        
        # Handle pandas Index
        elif isinstance(obj, pd.Index):
            return obj.tolist()
        
        # Default to base class encoder
        return super().default(obj)


def safe_json_dumps(data, **kwargs):
    """Safely dump data to JSON string."""
    return json.dumps(data, cls=CustomJSONEncoder, **kwargs)


def safe_json_dump(data, fp, **kwargs):
    """Safely dump data to JSON file."""
    return json.dump(data, fp, cls=CustomJSONEncoder, **kwargs)